import { beforeEach, describe, expect, it } from "vitest";
import "../../Functions/Ecran.js";

const triggerDomReady = () => {
  document.dispatchEvent(new Event("DOMContentLoaded"));
};

const buildTable = () => {
  document.body.innerHTML = `
    <table id="serigraphie-table">
      <thead>
        <tr>
          <th>Col A<br><input class="filter-input" data-column="0" /></th>
          <th>Col B<br><input class="filter-input" data-column="1" /></th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Alpha</td><td>100</td></tr>
        <tr><td>Beta</td><td>200</td></tr>
        <tr><td>Gamma</td><td>201</td></tr>
      </tbody>
    </table>
  `;
};

const getRows = () => Array.from(document.querySelectorAll("tbody tr"));
const cellText = (row, col) => row.cells[col].textContent.trim();

describe("Ecran.js filtering", () => {
  beforeEach(() => {
    buildTable();
    triggerDomReady();
  });

  it("filters rows based on the first filter", () => {
    const [refFilter] = document.querySelectorAll(".filter-input");
    refFilter.value = "alp";
    refFilter.dispatchEvent(new Event("input", { bubbles: true }));

    const rows = getRows();
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

    const rows = getRows();
    expect(rows[0].style.display).toBe("");
    expect(rows[1].style.display).toBe("");
    expect(rows[2].style.display).toBe("none");
  });
});

describe("Ecran.js sorting", () => {
  beforeEach(() => {
    buildTable();
    triggerDomReady();
  });

  it("sorts column ascending on first click", () => {
    document.querySelector("thead th").click();
    const rows = getRows();
    expect(cellText(rows[0], 0)).toBe("Alpha");
    expect(cellText(rows[1], 0)).toBe("Beta");
    expect(cellText(rows[2], 0)).toBe("Gamma");
  });

  it("sorts column descending on second click", () => {
    const th = document.querySelector("thead th");
    th.click();
    th.click();
    const rows = getRows();
    expect(cellText(rows[0], 0)).toBe("Gamma");
    expect(cellText(rows[1], 0)).toBe("Beta");
    expect(cellText(rows[2], 0)).toBe("Alpha");
  });

  it("restores original order on third click", () => {
    const th = document.querySelector("thead th");
    th.click();
    th.click();
    th.click();
    const rows = getRows();
    expect(cellText(rows[0], 0)).toBe("Alpha");
    expect(cellText(rows[1], 0)).toBe("Beta");
    expect(cellText(rows[2], 0)).toBe("Gamma");
  });

  it("sorts numerically on numeric column ascending", () => {
    const th = document.querySelectorAll("thead th")[1];
    th.click();
    const rows = getRows();
    expect(cellText(rows[0], 1)).toBe("100");
    expect(cellText(rows[1], 1)).toBe("200");
    expect(cellText(rows[2], 1)).toBe("201");
  });

  it("sorts numerically on numeric column descending", () => {
    const th = document.querySelectorAll("thead th")[1];
    th.click();
    th.click();
    const rows = getRows();
    expect(cellText(rows[0], 1)).toBe("201");
    expect(cellText(rows[1], 1)).toBe("200");
    expect(cellText(rows[2], 1)).toBe("100");
  });

  it("sets data-sort attribute correctly", () => {
    const th = document.querySelector("thead th");
    th.click();
    expect(th.getAttribute("data-sort")).toBe("asc");
    th.click();
    expect(th.getAttribute("data-sort")).toBe("desc");
    th.click();
    expect(th.hasAttribute("data-sort")).toBe(false);
  });

  it("clears other columns sort indicator when sorting a new column", () => {
    const [th0, th1] = document.querySelectorAll("thead th");
    th0.click();
    th1.click();
    expect(th0.hasAttribute("data-sort")).toBe(false);
    expect(th1.getAttribute("data-sort")).toBe("asc");
  });
});
