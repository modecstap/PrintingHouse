import { useState } from "react";
import { INITIAL_DATA } from "./utils/InitialData"
import EconomicSection from "./sections/EconomicSection";
import EditionSection from "./sections/EditionSection";
import OperationSection from "./sections/OperationSection";
import PrintingSection from "./sections/PrintingSection";

export default function MultiLineCalculator({
  initial_data = {},
  hideActionButtons = false,
}) {
  const [formData, setFormData] = useState(() => ({
    ...INITIAL_DATA,
    ...initial_data,
  }));

  return (
    <>
      <PrintingSection formData={formData} setFormData={setFormData} />
      <EditionSection
        formData={formData}
        setFormData={setFormData}
        hideActionButtons={hideActionButtons}
      />
      <OperationSection formData={formData} setFormData={setFormData} />
      <EconomicSection formData={formData} setFormData={setFormData} />
    </>
  );
}