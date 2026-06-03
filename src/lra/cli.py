import typer
from lra.agent import main

app = typer.Typer(no_args_is_help=True)

@app.callback()
def callback() -> None:
    pass

@app.command()
def research(
    domain: str = typer.Option(..., "--domain", help="Company domain to research"),
    output: str = typer.Option(None, "--output", help="Output file path")
) -> None:
    result = main(domain)
    
    if output:
        with open(output, "w") as file:
            file.write(result.model_dump_json(indent=2))
    else:
        print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    app()