import { useEffect, useState } from "react";
import FlexForm from "./components/FlexForm";
import PrintingSection from "./sections/PrintingSection";
import OperationSection from "./sections/OperationSection";
import EconomicSection from "./sections/EconomicSection";
import EditionSection from "./sections/EditionSection";


export default function MultiLineCalculator({
  initial_data = {},
  hideActionButtons = false,
}) {
  const INITIAL_DATA = {
    creation_date: new Date().toISOString(),
    comment: "",
    unit_count: 1,
    printings: [
      {
        edition: {
          count: 0,
          list_size: { width: 420, height: 297, bleeds: 0 },
          density: 80,
          chroma: 1,
          lamination: 1,
          die_cutting: false,
        },
        production: {},
        comment: "",
      },
    ],
    operations: [
      {
        name: "",
        cost: 0,
        description: "",
      },
    ],
    economy: {
      tax_rate: 0.93,
      markup: 80,
    },
  };

  const [formData, setFormData] = useState(() => ({
    ...INITIAL_DATA,
    ...initial_data,
  }));

  return (
    <>
      <PrintingSection formData={formData} setFormData={setFormData} />
      <OperationSection formData={formData} setFormData={setFormData} />
      <EconomicSection formData={formData} setFormData={setFormData} />
      <EditionSection
        formData={formData}
        setFormData={setFormData}
        hideActionButtons={hideActionButtons}
      />
    </>
  );
}

