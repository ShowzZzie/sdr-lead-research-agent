import typer
from lra.agent import main
import asyncio

app = typer.Typer(no_args_is_help=True)

@app.callback()
def callback() -> None:
    pass

@app.command()
def research(
    domain: str = typer.Option(..., "--domain", help="Company domain to research"),
    use_cache: bool = typer.Option(False, "--use-cache", help="Should app look through stored profiles before calling the agent"),
    output: str = typer.Option(None, "--output", help="Output file path")
) -> None:
    result = asyncio.run(main(domain, use_cache=use_cache))
    
    if output:
        with open(output, "w") as file:
            file.write(result.model_dump_json(indent=2))
    else:
        print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    app()