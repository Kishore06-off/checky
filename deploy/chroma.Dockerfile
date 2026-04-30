FROM chromadb/chroma:latest

EXPOSE 8001

ENV CHROMA_SERVER_HOST=0.0.0.0
ENV CHROMA_SERVER_HTTP_PORT=8001
ENV CHROMA_LOG_VERBOSE=INFO

CMD ["chroma-server", "--host", "0.0.0.0", "--port", "8001"]
