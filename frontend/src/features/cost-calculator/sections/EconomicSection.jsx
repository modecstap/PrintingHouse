import { useState } from "react";
import FlexForm from "../components/FlexForm";


const ECONOMY_FIELDS = [
  {
    label: "Налоговая ставка",
    path: "economy.tax_rate",
    type: "number",
    step: 0.01,
    valueParser: Number,
  },
  {
    label: "Наценка",
    path: "economy.markup",
    type: "number",
    step: 0.01,
    valueParser: Number,
  },
];


export default function EconomicSection({formData, setFormData}){
    return(
    <section className="calculator-container">
        <h2>Экономика</h2>
        <FlexForm fields={ECONOMY_FIELDS} formData={formData} setFormData={setFormData} />
    </section>
    )
}