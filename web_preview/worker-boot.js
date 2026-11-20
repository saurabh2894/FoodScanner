/* Boot script for the tesseract.js worker, published as tess/worker-boot.js.
 *
 * The artifact viewer's file server refuses .gz files (HTTP 415), but serves text files. This wrapper
 * answers the worker's request for eng.traineddata.gz from eng.traineddata.b64.txt (the same bytes,
 * base64), then loads the unmodified tesseract.js worker. Nothing leaves the page's own files. */
(function () {
  var realFetch = self.fetch.bind(self);
  self.fetch = function (url, init) {
    if (/\/eng\.traineddata\.gz(\?.*)?$/.test(String(url))) {
      return realFetch(new URL("eng.traineddata.b64.txt", self.location.href).href).then(function (r) {
        if (!r.ok) return new Response("language data missing: HTTP " + r.status, { status: 500 });
        return r.text().then(function (t) {
          var bin = atob(t.replace(/\s+/g, ""));
          var bytes = new Uint8Array(bin.length);
          for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
          return new Response(bytes, { status: 200 });
        });
      });
    }
    return realFetch(url, init);
  };
  importScripts("worker.min.js");
})();
