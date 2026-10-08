from reportlens.services.rag.document_parser import DocumentParser
from pathlib import Path
import asyncio

async def main():
    parser = DocumentParser()

    await parser.ingest_doc(
        file_paths=[
            "/Users/sriman/Documents/ReportLensCodeBase/ReportLens/sample_documents/attention_paper.pdf",
            "/Users/sriman/Documents/ReportLensCodeBase/ReportLens/sample_documents/docling_paper.pdf"
        ]
    )

if __name__ == "__main__":
    asyncio.run(main())