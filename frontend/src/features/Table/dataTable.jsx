import React from 'react';
import styles from './DataTable.module.css';
import { usePagination } from './hooks/usePagination';
import { Pagination } from './ui/Pagination';

const DataTable = ({
  columns,
  data,
  actions,
  rowsPerPage = 10,
  getRowId = (row) => row.id,
}) => {
  const {
    page,
    totalPages,
    paginatedData,
    changePage,
  } = usePagination(data, rowsPerPage);

  const columnCount = columns.length + (actions ? 1 : 0);

  return (
    <div className={styles.container}>
      <div className={styles.table}>
        {/* Header */}
        <div
          className={`${styles.row} ${styles.header}`}
          style={{ '--columns': columnCount }}
        >
          {columns.map((col) => (
            <div key={col.key} className={styles.cell}>
              {col.label}
            </div>
          ))}

          {actions && <div className={styles.cell}>Actions</div>}
        </div>

        {/* Rows */}
        {paginatedData.map((row) => (
          <div
            key={getRowId(row)}
            className={styles.row}
            style={{ '--columns': columnCount }}
          >
            {columns.map((col) => (
              <div key={col.key} className={styles.cell}>
                {col.render
                  ? col.render(row[col.key], row)
                  : row[col.key]}
              </div>
            ))}

            {actions && (
              <div className={styles.actions}>
                {actions.map((action, idx) => (
                  <React.Fragment key={idx}>
                    {action.render(row)}
                  </React.Fragment>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <Pagination
        page={page}
        totalPages={totalPages}
        onChange={changePage}
      />
    </div>
  );
};

export default DataTable;