"""Launch the local Gradio application."""

from __future__ import annotations

import os

from .ui import APP_CSS, build_app


def main() -> None:
    host = os.getenv("PAE_HOST", "127.0.0.1")
    port = int(os.getenv("PAE_PORT", "7860"))
    inbrowser = os.getenv("PAE_INBROWSER", "1").lower() not in {"0", "false", "no"}
    build_app().queue(default_concurrency_limit=1).launch(
        server_name=host,
        server_port=port,
        share=False,
        inbrowser=inbrowser,
        show_error=True,
        css=APP_CSS,
    )


if __name__ == "__main__":
    main()
