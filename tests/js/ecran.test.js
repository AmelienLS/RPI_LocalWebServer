import { beforeEach, describe, expect, it } from "vitest";
import "../../Functions/Ecran.js";

const triggerDomReady = () => {
  document.dispatchEvent(new Event("DOMContentLoaded"));
};

const buildTable = () => {
  document.body.innerHTML = `
    <input class="filter-input" data-column="0" />
    <input class="filter-input" data-column="1" />
    <table id="serigraphie-table">
      <tbody>
        <tr><td>Alpha</td><td>100</td></tr>
        <tr><td>Beta</td><td>200</td></tr>
        <tr><td>Gamma</td><td>201</td></tr>
      </tbody>
    </table>
  `;
};

describe("Ecran.js filtering", () => {
  beforeEach(() => {
    buildTable();
    triggerDomReady();
  });

  it("filters rows based on the first filter", () => {
    const [refFilter] = document.querySelectorAll(".filter-input");
    refFilter.value = "alp";
    refFilter.dispatchEvent(new Event("input", { bubbles: true }));

    const rows = Array.from(document.querySelectorAll("tbody tr"));
    expect(rows[0].style.display).toBe("");
    expect(rows[1].style.display).toBe("none");
    expect(rows[2].style.display).toBe("none");
  });

  it("applies combined filters on multiple columns", () => {
    const filters = document.querySelectorAll(".filter-input");
    filters[0].value = "a";
    filters[0].dispatchEvent(new Event("input", { bubbles: true }));

    filters[1].value = "00";
    filters[1].dispatchEvent(new Event("input", { bubbles: true }));

    const rows = Array.from(document.querySelectorAll("tbody tr"));
    expect(rows[0].style.display).toBe("");
    expect(rows[1].style.display).toBe("");
    expect(rows[2].style.display).toBe("none");
  });
});
