import { useState } from 'react';

export const usePagination = (data, rowsPerPage) => {
  const [page, setPage] = useState(1);

  const totalPages = Math.max(1, Math.ceil(data.length / rowsPerPage));

  const paginatedData = data.slice(
    (page - 1) * rowsPerPage,
    page * rowsPerPage
  );

  const changePage = (p) => {
    if (p >= 1 && p <= totalPages) {
      setPage(p);
    }
  };

  return {
    page,
    totalPages,
    paginatedData,
    changePage,
  };
};