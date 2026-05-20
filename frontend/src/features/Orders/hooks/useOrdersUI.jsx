import { useState } from "react";

export const useOrdersUI = () => {
  const [selectedItem, setSelectedItem] = useState(null);
  const [statusTarget, setStatusTarget] = useState(null);

  return {
    selectedItem,
    openModal: (item, showActions = false) =>
      setSelectedItem({ item, showActions }),
    closeModal: () => setSelectedItem(null),

    statusTarget,
    setStatusTarget,
  };
};
