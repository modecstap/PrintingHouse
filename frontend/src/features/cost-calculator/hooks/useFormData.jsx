import { useState } from "react";
import { defaultEdition, defaultProduction } from "../../../constants/defaults";

export const useFormData = (initialEdition = {}, initialProduction = {}) => {
  const [formData, setFormData] = useState({
    edition: { ...defaultEdition, ...initialEdition },
    production: { ...defaultProduction, ...initialProduction },
  });

  const updateSection = (section, values) => {
    setFormData((prev) => ({
      ...prev,
      [section]: { ...prev[section], ...values },
    }));
  };

  return [formData, updateSection];
};
