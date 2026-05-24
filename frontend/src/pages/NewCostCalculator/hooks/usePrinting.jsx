import { useEffect } from "react";
import { calculatorService } from "../services/calculatorService";

export const usePrinting = (setFormData) => {
  useEffect(() => {
    loadReference();
  }, []);

  const loadReference = async () => {
    const data = await calculatorService.getProductionReference();

    setFormData(prev => ({
      ...prev,
      printings: prev.printings.map(p => ({
        ...p,
        production: data,
      })),
    }));
  };

  return { loadReference };
};