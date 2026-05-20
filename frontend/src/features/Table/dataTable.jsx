import React, { useState } from "react";
import "./dataTable.css";

export default function DataTable({
  columns,
  data,
  actions,
  rowsPerPage = 10
}) {
  const [page, setPage] = useState(1);

  const totalPages = Math.ceil(data.length / rowsPerPage);

  const paginatedData = data.slice(
    (page - 1) * rowsPerPage,
    page * rowsPerPage
  );

  const changePage = (p) => {
    if (p >= 1 && p <= totalPages) {
      setPage(p);
    }
  };

  const renderPages = () => {
    const pages = [];

    for (let i = 1; i <= totalPages; i++) {
      if (
        i === 1 ||
        i === totalPages ||
        Math.abs(i - page) <= 2
      ) {
        pages.push(
          <button
            key={i}
            onClick={() => changePage(i)}
            className={i === page ? "active" : ""}
          >
            {i}
          </button>
        );
      } else if (
        (i === page - 3 && i > 1) ||
        (i === page + 3 && i < totalPages)
      ) {
        pages.push(<span key={i}>...</span>);
      }
    }

    return pages;
  };

  return (
    <div className="table-container">
      {/* Table */}
      <div className="table">
        {/* Header row */}
        <div
          className="item-row header-row"
          style={{
            gridTemplateColumns: `repeat(${columns.length + (actions ? 1 : 0)}, 1fr)`
          }}
        >
          {columns.map((col) => (
            <div key={col.key} className="item-field">
              <strong>{col.label}</strong>
            </div>
          ))}
          {actions && (
            <div className="item-field">
              <strong>Actions</strong>
            </div>
          )}
        </div>

        {/* Data rows */}
        {paginatedData.map((row) => (
          <div
            key={row.id}
            className="item-row"
            style={{
              gridTemplateColumns: `repeat(${columns.length + (actions ? 1 : 0)}, 1fr)`
            }}
          >
            {columns.map((col) => (
              <div key={col.key} className="item-field">
                {row[col.key]}
              </div>
            ))}

            {actions && (
              <div className="item-actions">
                {actions.map((action, idx) => (
                  action.render ? (
                    <React.Fragment key={idx}>
                      {action.render(row)}
                    </React.Fragment>
                  ) : (
                    <button
                      key={idx}
                      className={action.className || ""}
                      onClick={() => action.onClick(row)}
                    >
                      {action.icon || action.label}
                    </button>
                  )
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="pagination">
        <button onClick={() => changePage(1)}>{"<<"}</button>
        <button onClick={() => changePage(page - 1)}>{"<"}</button>

        {renderPages()}

        <button onClick={() => changePage(page + 1)}>{">"}</button>
        <button onClick={() => changePage(totalPages)}>{">>"}</button>
      </div>
    </div>
  );
}