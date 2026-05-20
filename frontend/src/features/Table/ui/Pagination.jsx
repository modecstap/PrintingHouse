import React from 'react';
import styles from '../DataTable.module.css';

export const Pagination = ({ page, totalPages, onChange }) => {
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
            onClick={() => onChange(i)}
            className={i === page ? styles.active : ''}
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
    <div className={styles.pagination}>
      <button onClick={() => onChange(1)}>{"<<"}</button>
      <button onClick={() => onChange(page - 1)}>{"<"}</button>

      {renderPages()}

      <button onClick={() => onChange(page + 1)}>{">"}</button>
      <button onClick={() => onChange(totalPages)}>{">>"}</button>
    </div>
  );
};