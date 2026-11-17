// Buoi 5: kiem thu ham api() voi fetch gia lap (khong goi Backend/PostgreSQL that).
// Chay: npm test (dung trong thu muc frontend/).
import { test, afterEach } from "node:test";
import assert from "node:assert/strict";
import { api } from "../src/api.js";

const BASE_URL = "http://127.0.0.1:8000";
const realFetch = globalThis.fetch;

// Thay fetch bang ham gia lap, ghi lai URL va options cua lan goi gan nhat.
function mockFetch(handler) {
  const calls = [];
  globalThis.fetch = async (url, options) => {
    calls.push({ url, options });
    return handler(url, options);
  };
  return calls;
}

function jsonResponse(status, data) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

afterEach(() => {
  globalThis.fetch = realFetch;
});

test("1. GET 200 tra ve JSON va goi dung URL, khong gui body", async () => {
  const sections = [{ class_id: "WEB-01", capacity: 3, enrolled: 2, remaining: 1 }];
  const calls = mockFetch(() => jsonResponse(200, sections));

  const data = await api("/sections");

  assert.deepEqual(data, sections);
  assert.equal(calls[0].url, `${BASE_URL}/sections`);
  assert.equal(calls[0].options.method, "GET");
  assert.equal(calls[0].options.body, undefined);
  assert.deepEqual(calls[0].options.headers, {});
});

test("2. POST gui body JSON voi Content-Type va nhan 201", async () => {
  const created = { student_id: "22000004", class_section_id: "WEB-01" };
  const calls = mockFetch(() => jsonResponse(201, created));

  const data = await api("/enrollments", { method: "POST", body: created });

  assert.deepEqual(data, created);
  assert.equal(calls[0].options.method, "POST");
  assert.equal(calls[0].options.headers["Content-Type"], "application/json");
  assert.deepEqual(JSON.parse(calls[0].options.body), created);
});

test("3. DELETE 204 tra ve null, khong doc JSON", async () => {
  mockFetch(() => new Response(null, { status: 204 }));

  const data = await api("/enrollments/22000004/WEB-01", { method: "DELETE" });

  assert.equal(data, null);
});

test("4. 404 voi detail dang chuoi thanh Error co status", async () => {
  mockFetch(() => jsonResponse(404, { detail: "Khong tim thay sinh vien" }));

  await assert.rejects(api("/students/99999999/enrollments"), (error) => {
    assert.equal(error.status, 404);
    assert.equal(error.message, "HTTP 404: Khong tim thay sinh vien");
    return true;
  });
});

test("5. 409 khi lop het cho giu nguyen detail cua Backend", async () => {
  mockFetch(() => jsonResponse(409, { detail: "Lop RACE-01 da het cho" }));

  await assert.rejects(
    api("/enrollments", {
      method: "POST",
      body: { student_id: "22000004", class_section_id: "RACE-01" },
    }),
    (error) => {
      assert.equal(error.status, 409);
      assert.match(error.message, /^HTTP 409: Lop RACE-01 da het cho$/);
      return true;
    },
  );
});

test("6. 422 voi detail dang danh sach duoc ghep thanh mot chuoi", async () => {
  mockFetch(() =>
    jsonResponse(422, {
      detail: [
        { loc: ["body", "student_id"], msg: "Field required" },
        { loc: ["body", "class_section_id"], msg: "Field required" },
      ],
    }),
  );

  await assert.rejects(api("/enrollments", { method: "POST", body: {} }), (error) => {
    assert.equal(error.status, 422);
    assert.equal(error.message, "HTTP 422: Field required; Field required");
    return true;
  });
});

test("7. Phan hoi khong phai JSON bao loi ro rang", async () => {
  mockFetch(() => new Response("<html>Internal Server Error</html>", { status: 500 }));

  await assert.rejects(api("/sections"), {
    message: "HTTP 500: phản hồi không phải JSON.",
  });
});

test("8. Mat ket noi bao loi Backend/CORS; AbortError duoc nem lai nguyen ven", async () => {
  mockFetch(() => {
    throw new TypeError("Failed to fetch");
  });
  await assert.rejects(api("/sections"), (error) => {
    assert.match(error.message, /Không nhận được phản hồi API/);
    assert.equal(error.status, undefined);
    return true;
  });

  const controller = new AbortController();
  mockFetch(() => {
    throw new DOMException("The operation was aborted.", "AbortError");
  });
  controller.abort();
  await assert.rejects(api("/sections", { signal: controller.signal }), {
    name: "AbortError",
  });
});
