import { useState } from "react";
import FlexForm from "../components/FlexForm";


const operationFields = (index) => [
  {
    label: "Название операции",
    path: `operations[${index}].name`,
    type: "text",
  },
  {
    label: "Стоимость",
    path: `operations[${index}].cost`,
    type: "number",
    valueParser: Number,
  },
  {
    label: "Описание",
    path: `operations[${index}].description`,
    type: "text",
  },
];

const newOperation = () => ({
    name: "",
    cost: 0,
    description: "",
});



export default function OperationSection({formData, setFormData}){
    
    const addOperation = () => setFormData((d) => ({ ...d, operations: [...d.operations, newOperation()] }));


    const removeOperation = (index) => {
    setFormData(d => ({
        ...d,
        operations: d.operations.filter((_, i) => i !== index),
    }));
    };

    return(
    <section className="calculator-container">
        <h2>Дополнительные работы</h2>
        {formData.operations.map((_, i) => (
            <>
            <div key={i} className="sub-block">
                <FlexForm
                fields={operationFields(i)}
                formData={formData}
                setFormData={setFormData}
                />
            </div>
            <button
                className="btn btn-primary"
                onClick={() => removeOperation(i)}
            >
                Удалить
            </button>
            <div className="separator"></div>
            </>
        ))}
        <button className="btn btn-primary" onClick={addOperation}>
            + Добавить работу
        </button>
    </section>
    )
}