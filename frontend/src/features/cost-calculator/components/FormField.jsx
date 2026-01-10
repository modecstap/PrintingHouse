function parsePath(path) {
  return path
    .replace(/\[(\d+)\]/g, ".$1")
    .split(".")
    .filter(Boolean)
    .map((p) => (p.match(/^\d+$/) ? Number(p) : p));
}

function getByPath(obj, path) {
  const keys = Array.isArray(path) ? path : parsePath(path);

  return keys.reduce((acc, key) => {
    if (acc == null) return undefined;
    return acc[key];
  }, obj);
}

function updateByPath(obj, path, value) {
  const keys = parsePath(path);
  const result = structuredClone(obj);

  let current = result;

  keys.forEach((key, index) => {
    if (index === keys.length - 1) {
      current[key] = value; // сохраняем значение как есть
      return;
    }

    if (current[key] == null) {
      current[key] = typeof keys[index + 1] === "number" ? [] : {};
    }

    current = current[key];
  });

  return result;
}

export default function FormField({
  label,
  path,
  data,
  setData,
  type = "text",
  step,
  options = {},
  valueParser,
}) {
  const value = getByPath(data, path);

  const handleChange = (e) => {
    let val = e.target.value;

    if (type === "number") {
      val = val;
    } else if (type === "select" && valueParser) {
      val = valueParser(val);
    }

    setData((prev) => updateByPath(prev, path, val));
  };

  return (
    <div className="form-tile">
      <label>{label}</label>

      {type === "select" ? (
        <select value={value ?? ""} onChange={handleChange}>
          {options?.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      ) : type === "textarea" ? (
        <textarea
          rows={options.rows ?? 3}
          value={value ?? ""}
          onChange={handleChange}
        />
      ) : (
        <input
          type={type}
          step={step}
          value={value ?? ""}
          onChange={handleChange}
        />
      )}
    </div>
  );
}
