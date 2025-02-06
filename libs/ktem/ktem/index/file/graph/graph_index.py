from typing import Any

from ktem.index.file import FileIndex

from ..base import BaseFileIndexIndexing, BaseFileIndexRetriever
from .pipelines import GraphRAGIndexingPipeline, GraphRAGRetrieverPipeline


class GraphRAGIndex(FileIndex):
    def _setup_indexing_cls(self):
        self._indexing_pipeline_cls = GraphRAGIndexingPipeline

    def _setup_retriever_cls(self):
        self._retriever_pipeline_cls = [GraphRAGRetrieverPipeline]

    def has_graph_index(self, file_id: str) -> bool:
        """Check if a graph index exists for the given file ID"""
        from ktem.db.models import engine
        from sqlmodel import Session, select
        import logging

        logger = logging.getLogger(__name__)
        
        # Skip checking for 'all' as it's a special case
        if str(file_id).lower() == 'all':
            return True
            
        try:
            with Session(engine) as session:
                # Try different formats of the file_id
                possible_ids = [
                    file_id,
                    str(file_id),
                    int(str(file_id)) if str(file_id).isdigit() else None
                ]
                possible_ids = [pid for pid in possible_ids if pid is not None]
                
                for pid in possible_ids:
                    graph_id = session.exec(
                        select(self._resources["Index"].target_id)
                        .where(self._resources["Index"].source_id == pid)
                        .where(self._resources["Index"].relation_type == "graph")
                    ).first()
                    if graph_id:
                        logger.debug(f"Found graph index for file_id: {pid}")
                        return True
                        
                logger.warning(f"No graph index found for any format of file_id: {file_id}")
                return False
        except Exception as e:
            logger.error(f"Error checking graph index for file_id {file_id}: {e}")
            return False

    def get_indexing_pipeline(self, settings, user_id) -> BaseFileIndexIndexing:
        """Define the interface of the indexing pipeline"""

        obj = super().get_indexing_pipeline(settings, user_id)
        # disable vectorstore for this kind of Index
        obj.VS = None

        return obj

    def get_retriever_pipelines(
        self, settings: dict, user_id: int, selected: Any = None
    ) -> list["BaseFileIndexRetriever"]:
        _, file_ids, _ = selected if selected else (None, [], None)
        
        # If no files are explicitly selected or empty file_ids, get all available file IDs
        if not file_ids:
            from ktem.db.models import engine
            from sqlmodel import Session, select
            with Session(engine) as session:
                statement = select(self._resources["Source"].id)
                if self.config.get("private", False):
                    statement = statement.where(self._resources["Source"].user == user_id)
                results = session.execute(statement).all()
                file_ids = [str(id[0]) for id in results]  # Convert IDs to strings

        # Ensure file_ids is not empty and contains valid strings
        if not file_ids:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("No files selected for retrieval, using all available files")
            with Session(engine) as session:
                statement = select(self._resources["Source"].id)
                if self.config.get("private", False):
                    statement = statement.where(self._resources["Source"].user == user_id)
                results = session.execute(statement).all()
                file_ids = [str(id[0]) for id in results]

        retrievers = [
            GraphRAGRetrieverPipeline(
                file_ids=file_ids,
                Index=self._resources["Index"],
            )
        ]

        return retrievers
