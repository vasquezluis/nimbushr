#!/usr/bin/env python3
"""
Config Script
Entry point for running the RAG ingestion pipeline
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from rag.ingest.ingest import run_complete_ingestion_pipeline

print("🚀 Starting setup script...", flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"Current directory: {os.getcwd()}", flush=True)

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  Warning: OPENAI_API_KEY not found in environment", flush=True)
    print("Please make sure your .env file contains OPENAI_API_KEY", flush=True)


def main():
    print("\n" + "=" * 60, flush=True)
    print("SETUP PIPELINE", flush=True)
    print("=" * 60 + "\n", flush=True)

    parser = argparse.ArgumentParser(description="Run RAG ingestion on all documents")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="chroma_db",
        help="Directory to store the vector database (default: chroma_db)",
    )

    args = parser.parse_args()

    print(f"💾 Output Directory: {args.output_dir}", flush=True)
    print(flush=True)

    # Run the pipeline
    try:
        print("Starting pipeline execution...", flush=True)
        db = run_complete_ingestion_pipeline(persist_directory=args.output_dir)
        print(f"\n✅ Success! Vector store saved to: {args.output_dir}", flush=True)
        return 0
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}", flush=True)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        print(f"\nScript completed with exit code: {exit_code}", flush=True)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user", flush=True)
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", flush=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)
