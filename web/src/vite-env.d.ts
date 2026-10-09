/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Backend origin, e.g. http://localhost:8000. Empty = same-origin via proxy. */
  readonly VITE_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
