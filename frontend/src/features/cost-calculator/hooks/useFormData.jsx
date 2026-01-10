import { useEffect, useState } from "react";
import { defaultEdition, defaultProduction, defaultEconomy } from "../../../constants/defaults";
import { BackendIP } from "../../../constants/BackendIP";

export const useFormData = (
  initialEdition = {},
  initialProduction = {},
  initialEconomy = {}
) => {
  const [formData, setFormData] = useState({
    printings: [
      {
        edition: { ...defaultEdition, ...initialEdition },
        production: { ...defaultProduction, ...initialProduction }
      }
    ],
    economy: { ...defaultEconomy, ...initialEconomy },
  });

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
          printings: prev.printings.map((printing, index) =>
            index === 0
              ? {
                  ...printing,
                  production: {
                    ...defaultProduction,
                    ...data,
                  },
                }
              : printing
          ),
        }));
      } catch (err) {
        console.error("Failed to load production reference", err);
      }
    };

    loadProduction();
  }, []);


  return [formData, setFormData];
};
