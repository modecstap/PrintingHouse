import React from "react";
import AdvancedSection from "./AdvancedSection";
import ConsealedForm from "./ConsealedForm";

export default function AdvancedFormSection({ open, formData, onFormChange }) {
  return (
    <AdvancedSection open={open}>
      <div className="advanced-content">
        <ConsealedForm data={formData} onChange={onFormChange} />
      </div>
    </AdvancedSection>
  );
}
