import { useState } from "react";
import { useAsyncAction } from "../../hooks/useAsyncAction";
import FlexForm from "../generic/flex-form/flex-form";
import Button from "../generic/button/button";

import styles from "./auth.module.css";

const fields = [
  {
    label: "Логин",
    path: "username",
    type: "text",
  },
  {
    label: "Пароль",
    path: "password",
    type: "password",
  },
];

const Auth = () => {
  const { loading, error, successMsg, execute } = useAsyncAction();

  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const onSubmit = async (e) => {
    e.preventDefault();

    const res = await execute(
      "/auth/token",
      {
        username: formData.username,
        password: formData.password,
      },
      { method: "POST" }
    );

    if (res?.access_token) {
      localStorage.setItem("access_token", res.access_token);
      alert("ВХОД ВЫПОЛНЕН: ТОКЕН СОХРАНЁН");
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    alert("ВЫХОД ВЫПОЛНЕН");
  };

  return (
    <div className={styles.page}>
      <h2>Вход</h2>

      <form onSubmit={onSubmit}>
        <FlexForm
          fields={fields}
          formData={formData}
          setFormData={setFormData}
        />

        <div className={styles.buttonRow}>
          <Button type="submit" disabled={loading}>
            Войти
          </Button>

          <Button type="button" onClick={logout}>
            Выйти
          </Button>
        </div>

        {error && <div className={styles.error}>{error}</div>}
        {successMsg && <div className={styles.success}>{successMsg}</div>}
      </form>
    </div>
  );
};

export default Auth;
