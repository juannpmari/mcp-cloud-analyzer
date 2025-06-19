Local usage:

1. Run Localstack in docker container:
    ```
    docker run --rm -it -p 4566:4566 -p 4571:4571 localstack/localstack
    ```
2. Create dummy data (buckets + objects)
2. Run MCP server:
    ```
    mcp dev full/path/to/mcp-server/s3/server.py
    ```
    


Github mcp
1. Local mcp server using node package:

{
    "mcpServers": {
     "github": {
       "command": "npx",
       "args": [
         "-y",
         "@modelcontextprotocol/server-github"
       ]
     }
   }
}

  - esto usa stdio?
  - como resuelve la autenticacion? 
    - así como está no se autentica, solo accede a repos publicos, habria que ver cómo pasarle un auth token en los args
  - parece ser otro server que el oficial de github, xq tiene menos tools

2. Local using docker image:
    {
  "mcpServers": {
      "github-mcp-server": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "lll"
      }
    }
  }
}

  - esto usa stdio?
  - se deberia agregar el oauth flow antes para obtener el GITHUB_PERSONAL_ACCESS_TOKEN

3. Remote mcp server using npx and passing github PAT:
{
  "mcpServers": {
    "github-remote-server": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://api.githubcopilot.com/mcp/",
        "--header",
        "Authorization: Bearer GITHUB_PERSONAL_ACCESS_TOKEN"
    ],
      "disabled": false
    }
  }
}
  - esto usa sse?
  - sin el authorization tira 401 (no se autentica al server), porque la opción 1 sí?
    - porque es local, no necesita autenticarse al server, aunque sin el token despues no puede acceder a repos privados
  - se puede hacer con oauth? probar en vscode
    - done

- Probar corriendo los server con agente ClientSession (en vez de cascade), y listar las tools
    - done
- como sería la auth en este caso? se puede integrar OAuth?
    - done