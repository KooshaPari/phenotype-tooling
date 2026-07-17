{
  "mcpServers": {
    "mcp-installer": {
      "command": "npx",
      "args": [
        "@anaisbetts/mcp-installer"
      ]
    },
    "riza-mcp": {
      "command": "npx",
      "args": [
        "@riza-io/riza-mcp"
      ],
      "env": {
        "RIZA_API_KEY": "sss"
      }
    },
    "server-filesystem": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-filesystem",
        "/Users/kooshapari/temp-PRODVERCEL/"
      ]
    },
    "server-memory": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-memory"
      ]
    },
    "playwright-mcp-server": {
      "command": "npx",
      "args": [
        "@executeautomation/playwright-mcp-server",
        "-y"
      ]
    },
    "server-sequential-thinking": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    },
    "server-puppeteer": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-puppeteer",
        "-y"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "ssss"
      }
    },
    "server-everything": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-everything"
      ]
    },
    "git": {
      "command": "uvx",
      "args": [
        "mcp-server-git",
        "--repository",
        "path/to/git/repo"
      ]
    },
    "server-github": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-github"
      ]
    },
    "fetch": {
      "command": "uvx",
      "args": [
        "mcp-server-fetch"
      ]
    },
    "server-postgres": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-postgres"
      ]
    },
    "mcp-gsuite": {
      "command": "uvx",
      "args": [
        "mcp-gsuite"
      ]
    },
    "gemini": {
      "command": "npx",
      "args": [
        "github:aliargun/mcp-server-gemini",
        "-y"
      ],
      "env": {
        "GEMINI_API_KEY": "ssss"
      }
    },
    "github:aliargun/mcp-server-gemini": {
      "command": "npx",
      "args": [
        "github:aliargun/mcp-server-gemini",
        "-y"
      ],
      "env": {
        "GEMINI_API_KEY": "ssss"
      }
    },
    "manus-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/kooshapari/manus-mcp",
        "run",
        "mcp_server.py"
      ]
    },
    "playwright-server": {
      "command": "npx",
      "args": [
        "playwright-server"
      ]
    },
    "mcp-server-youtube-transcript": {
      "command": "npx",
      "args": [
        "@kimtaeyoon83/mcp-server-youtube-transcript"
      ]
    },
    "mcp-server-apple-shortcuts": {
      "command": "npx",
      "args": [
        "mcp-server-apple-shortcuts"
      ]
    },
    "mcp-server-commands": {
      "command": "npx",
      "args": [
        "mcp-server-commands"
      ]
    },
    "mcp-shell-server": {
      "command": "uvx",
      "args": [
        "mcp-shell-server"
      ]
    },
    "mcp-google-sheets": {
      "command": "uvx",
      "args": [
        "mcp-google-sheets"
      ]
    },
    "mcp-server-sqlite": {
      "command": "uvx",
      "args": [
        "mcp-server-sqlite"
      ]
    },
    "supabase-mcp-server": {
      "command": "npx",
      "args": [
        "@joshuarileydev/supabase-mcp-server"
      ]
    },
    "firebase-mcp": {
      "command": "npx",
      "args": [
        "@gannonh/firebase-mcp"
      ]
    },
    "magic": {
      "command": "npx",
      "args": [
        "@21st-dev/magic"
      ]
    },
    "mcp-server-everything-search": {
      "command": "uvx",
      "args": [
        "mcp-server-everything-search"
      ]
    },
    "llm-context": {
      "command": "npx",
      "args": [
        "llm-context"
      ]
    },
    "memorymesh": {
        "command": "node",
        "args": ["/Users/kooshapari//memorymesh/dist/index.js"]
      },
    "cognee": {
      "command": "uvx",
      "args": [
        "cognee"
      ]
    },
    "mcp-ragdocs": {
      "command": "npx",
      "args": [
        "@hannesrudolph/mcp-ragdocs"
      ]
    },
    "mcp-summarizer": {
      "command": "npx",
      "args": [
        "mcp-summarizer"
      ]
    },
    "graphlit-mcp-server": {
      "command": "npx",
      "args": [
        "graphlit-mcp-server"
      ]
    },
    "server-google-maps": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-google-maps"
      ]
    },
    "osp_marketing_tools": {
               "command": "uvx",
               "args": [
                   "--from",
                   "git+https://github.com/open-strategy-partners/osp_marketing_tools@main",
                   "osp_marketing_tools"
               ]
           },
    "mcp-package-version": {
      "command": "npx",
      "args": [
        "mcp-package-version"
      ]
    },
    "postman": {
          "command": "node",
          "args": [
            "/Users/kooshapari/postman-mcp-server/build/index.js"
          ],
          "env": {
            "POSTMAN_API_KEY": "ZAME"
          }
        },
    "mcp-pandoc": {
      "command": "uvx",
      "args": [
        "mcp-pandoc"
      ]
    },
    "website-downloader": {
          "command": "node",
          "args": ["/Users/kooshapari/website-downloader/build/index.js"]
        },
    "sql-analyzer": {
             "command": "uv",
             "args": [
                 "--directory",
                 "/Users/kooshapari/mcp-server-sql-analyzer",
                 "run",
                 "mcp-server-sql-analyzer"
             ]
         },
    "mcp-server-multiverse": {
      "command": "npx",
      "args": [
        "@lamemind/mcp-server-multiverse"
      ]
    },
    "excel-mcp-server": {
      "command": "npx",
      "args": [
        "excel-mcp-server"
      ]
    },
    "mcpxcodebuild": {
      "command": "uvx",
      "args": [
        "mcpxcodebuild"
      ]
    },
    "serveMyAPI": {
         "command": "node",
         "args": [
           "/Users/kooshapari/serveMyAPI/dist/index.js"
         ]
       },
    "mcp-server-fetch": {
      "command": "uvx",
      "args": [
        "mcp-server-fetch"
      ]
    },
    "mcp-server-git": {
      "command": "uvx",
      "args": [
        "mcp-server-git"
      ]
    },

    "mindmap": {
      "command": "uvx",
      "args": [
        "mindmap-mcp-server",
        "--return-type",
        "html"
      ]
    },

    "mcp-git-ingest": {
                "command": "uvx",
                "args": ["--from", "git+https://github.com/adhikasp/mcp-git-ingest", "mcp-git-ingest"]
            },
    "mcp-server": {
      "command": "npx",
      "args": [
        "@makehq/mcp-server"
      ]
    },
    "actors-mcp-server": {
      "command": "npx",
      "args": [
        "@apify/actors-mcp-server"
      ]
    },

    "godoc": {
      "command": "/Users/kooshapari/godoc-mcp",
      "args": [],
      "env": {
        "GOPATH": "/Users/kooshapari/go",
        "GOMODCACHE": "/Users/kooshapari/go/pkg/mod"
      }
    },
    "mcp-graphql": {
      "command": "npx",
      "args": [
        "mcp-graphql"
      ]
    },
    "upsonic": {
      "command": "uvx",
      "args": [
        "upsonic"
      ]
    },
    "figma-developer-mcp": {
      "command": "npx",
      "args": [
        "figma-developer-mcp"
      ]
    },
    "docker-mcp": {
      "command": "uvx",
      "args": [
        "docker-mcp"
      ]
    },
    "xcode-mcp-server": {
      "command": "npx",
      "args": [
        "xcode-mcp-server"
      ]
    },
    "simulator-mcp-server": {
      "command": "npx",
      "args": [
        "@joshuarileydev/simulator-mcp-server"
      ]
    },
    "mcp-server-taskwarrior": {
      "command": "npx",
      "args": [
        "mcp-server-taskwarrior"
      ]
    },
    "replicate-flux-mcp": {
      "command": "npx",
      "args": [
        "replicate-flux-mcp"
      ]
    },
    "simulator": {
      "command": "npx",
      "args": [
        "y",
        "@joshuarileydev/mac-apps-launcher-mcp-server"
      ]
    },

    "wcgw": {
      "command": "uvx",
      "args": [
        "wcgw"
      ]
    },
    "jira-mcp-server": {
      "command": "npx",
      "args": [
        "jira-mcp-server"
      ]
    },
    "mcp-atlassian": {
      "command": "uvx",
      "args": [
        "mcp-atlassian"
      ]
    },
    "mcp-simple-timeserver": {
      "command": "uvx",
      "args": [
        "mcp-simple-timeserver"
      ]
    },
    "mcp-sequentialthinking-tools": {
      "command": "npx",
      "args": [
        "mcp-sequentialthinking-tools"
      ]
    },
    "agentql-mcp": {
      "command": "npx",
      "args": [
        "agentql-mcp"
      ]
    },

    "linear-mcp-server": {
      "command": "npx",
      "args": [
        "linear-mcp-server"
      ]
    },
    "mcp-server-kubernetes": {
      "command": "npx",
      "args": [
        "mcp-server-kubernetes"
      ]
    },
    "server-everart": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-everart"
      ]
    },
    "server-aws-kb-retrieval": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-aws-kb-retrieval"
      ]
    },
    "swift-mcp-gui": {
      "command": "/Users/kooshapari/.swiftpm/bin/swift-mcp-gui"
    },
    "omniparser_autogui_mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/kooshapari/omniparser-autogui-mcp",
        "run",
        "omniparser-autogui-mcp"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "OCR_LANG": "en"
      }
    },
    "todoist-mcp-server": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/cli@latest",
        "run",
        "@abhiz123/todoist-mcp-server",
        "--config",
        "\"{\\\"todoistApiToken\\\":\\\"ss\\\"}\""
      ]
    }
  }
}
