vcl 4.0;

backend default {
  .host = "run-gunicorn:8081";
}

sub vcl_backend_response {
  unset beresp.http.server;
}
