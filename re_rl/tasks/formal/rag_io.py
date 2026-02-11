"""
Shared helpers for tactic templates and RAG loading/building.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional, Tuple, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from re_rl.tasks.formal.lean_navigator.core import TacticTemplateExtractor


def _resolve_rag_mode(rag_model: str, nav_data: Path) -> Tuple[bool, Optional[str]]:
    use_trained_rag = False
    trained_model_path = None

    if rag_model == "trained":
        default_trained = nav_data / "trained_rag" / "bert_rag_model"
        if default_trained.exists():
            trained_model_path = str(default_trained)
            use_trained_rag = True
    elif rag_model != "sbert":
        maybe_path = Path(rag_model)
        if maybe_path.exists():
            trained_model_path = str(maybe_path)
            use_trained_rag = True

    return use_trained_rag, trained_model_path


def load_or_build_templates(
    nav_data: Path,
    repo_dir: Optional[Path] = None,
    print_fn: Optional[Callable[[str], None]] = None,
) -> "TacticTemplateExtractor":
    """
    Load cached tactic templates; if cache is absent and repo_dir provided, build.
    """
    log = print_fn or (lambda *_args, **_kwargs: None)
    templates_path = nav_data / "tactic_templates.json"

    # Ленивая загрузка: важно для Ray workers, чтобы не импортировать pantograph
    # до сброса uvloop policy внутри воркера.
    from re_rl.tasks.formal.lean_navigator.core import TacticTemplateExtractor
    extractor = TacticTemplateExtractor()
    if templates_path.exists():
        extractor.load(str(templates_path))
        return extractor

    if repo_dir is None:
        raise FileNotFoundError(f"Шаблоны не найдены: {templates_path}")

    log("Шаблоны не найдены — извлекаем из ast (один раз)...")
    extractor.extract_from_ast_dir(str(repo_dir))
    extractor.save(str(templates_path))
    return extractor


def load_or_build_rag(
    extractor: Any,
    nav_data: Path,
    rag_model: str,
    min_template_freq: int,
):
    """
    Build/load either SBERT RAG or trained-BERT RAG depending on rag_model.
    """
    use_trained_rag, trained_model_path = _resolve_rag_mode(rag_model, nav_data)

    if use_trained_rag:
        from re_rl.tasks.formal.lean_navigator.rag_trainer import TrainedTacticRAG
        trained_rag_index = nav_data / "trained_rag" / "trained_rag_index"
        rag = TrainedTacticRAG(model_path=trained_model_path)
        if (trained_rag_index / "faiss_l2.index").exists():
            rag.load(str(trained_rag_index))
        else:
            rag.build_index(extractor.templates, min_freq=min_template_freq)
            rag.save(str(trained_rag_index))
        return rag

    rag_path = nav_data / "rag_index"
    from re_rl.tasks.formal.lean_navigator.core import TacticRAG
    rag = TacticRAG(model_name="all-MiniLM-L6-v2")
    if (rag_path / "faiss.index").exists():
        rag.load(str(rag_path))
    else:
        rag.build_index(extractor.templates, min_freq=min_template_freq)
        rag.save(str(rag_path))
    return rag


def ensure_templates_and_rag_ready(
    nav_data: Path,
    repo_dir: Path,
    rag_model: str,
    min_template_freq: int,
) -> bool:
    """
    Ensure template cache and selected RAG index are ready.
    """
    extractor = load_or_build_templates(nav_data=nav_data, repo_dir=repo_dir)
    _ = load_or_build_rag(
        extractor=extractor,
        nav_data=nav_data,
        rag_model=rag_model,
        min_template_freq=min_template_freq,
    )
    return True
