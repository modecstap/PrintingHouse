import { useState } from "react";
import { useAsyncAction } from "../../hooks/useAsyncAction";
import FlexForm from "../../features/Form/FlexForm";

import styles from "./AuthPage.module.css"

const fields = [
  {
    label: "Имя пользователя",
    path: "username",
    type: "text",
  },
  {
    label: "Пароль",
    path: "password",
    type: "password",
  },
];

const AuthPage = () => {
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
      alert("Вход выполнен: токен сохранён");
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    alert("Выход выполнен");
  };

  return (
    <div className={styles.calculatorContainer}>
      <h2>Авторизация (JWT)</h2>

      <form
        onSubmit={onSubmit}
      >
        <FlexForm
          fields={fields}
          formData={formData}
          setFormData={setFormData}
        />

        <div className={styles.buttonRow}>
          <button type="submit" disabled={loading} className={`${styles.btn} ${styles.btnPrimary}`}>
            Войти
          </button>

          <button type="button" onClick={logout} className={`${styles.btn} ${styles.btnPrimary}`}>
            Выйти
          </button>
        </div>

        {error && <div style={{ color: "red" }}>{error}</div>}
        {successMsg && <div style={{ color: "green" }}>{successMsg}</div>}
      </form>
    </div>
  );
};

export default AuthPage;