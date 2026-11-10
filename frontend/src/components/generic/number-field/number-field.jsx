import { TextField } from "../text-field/text-field";

export function NumberField({ step = "1", min, max, ...props }) {
  return (
    <TextField {...props} type="number" step={step} min={min} max={max} />
  );
}
