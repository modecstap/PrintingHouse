import { useEffect, useState } from "react";
import { defaultEdition, defaultProduction } from "../../../constants/defaults";
import { BackendIP } from "../../../constants/BackendIP";

export const useFormData = (
  initialEdition = {},
  initialProduction = {}
) => {
  const [formData, setFormData] = useState({
    edition: { ...defaultEdition, ...initialEdition },
    production: { ...defaultProduction, ...initialProduction },
  });

  // ===== подгрузка production, если его нет =====
  useEffect(() => {
    const isProductionEmpty =
      !initialProduction ||
      Object.keys(initialProduction).length === 0;

    if (!isProductionEmpty) return;

    const loadProduction = async () => {
      try {
        const response = await fetch(
          `${BackendIP}/api/reference/production`,
          { method: "GET" }
        );

        if (!response.ok) return;

        const data = await response.json();

        setFormData((prev) => ({
          ...prev,
          production: {
            ...defaultProduction,
            ...data,
          },
        }));
      } catch (err) {
        console.error("Failed to load production reference", err);
      }
    };

    loadProduction();
  }, []); // ← важно: только при инициализации

  const updateSection = (section, values) => {
    setFormData((prev) => ({
      ...prev,
      [section]: { ...prev[section], ...values },
    }));
  };

  return [formData, updateSection];
};
