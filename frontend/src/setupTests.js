import "@testing-library/jest-dom";
import { webcrypto } from "crypto";

if (!globalThis.crypto?.randomUUID) {
  globalThis.crypto = webcrypto;
}
