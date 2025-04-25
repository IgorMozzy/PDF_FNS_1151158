document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("pdfForm");
  const allInputs = form.querySelectorAll("input, select");

  const checkbox = document.getElementById("same_person");
  const hiddenField = document.getElementById("same_person_hidden");

  const payerDocType = document.getElementById("payer_doc_type");
  const payerDocSeries = document.getElementById("payer_doc_series");
  const payerDocFields = document.querySelectorAll(".doc-hidden");

  const studentDocType = document.getElementById("student_doc_type");
  const studentDocSeries = document.getElementById("student_doc_series");
  const studentDocFields = document.querySelectorAll(".doc2-hidden");

  const studentHiddenFields = document.querySelectorAll(".student-hidden");

  // Восстановление значений из localStorage
  allInputs.forEach(input => {
    const saved = localStorage.getItem(input.name);
    if (saved !== null) {
      if (input.type === "checkbox") {
        input.checked = saved === "true";
      } else {
        input.value = saved;
      }
    }
  });

  // Сохранение значений в localStorage
  allInputs.forEach(input => {
    input.addEventListener("change", () => {
      if (input.type === "checkbox") {
        localStorage.setItem(input.name, input.checked);
      } else {
        localStorage.setItem(input.name, input.value);
      }
    });
  });

  // Очистка формы и хранилища
  document.getElementById("clearFormButton").addEventListener("click", () => {
    allInputs.forEach(input => {
      if (input.type === "checkbox") {
        input.checked = false;
      } else {
        input.value = "";
      }
      localStorage.removeItem(input.name);
    });

    // Принудительно сбросить отображение
    checkbox.checked = true;
    hiddenField.value = "1";
    toggleStudentFields();
    payerDocFields.forEach(el => el.classList.add("d-none"));
    studentDocFields.forEach(el => el.classList.add("d-none"));
  });

  // Функция показа/скрытия полей ученика и его документов
  function toggleStudentFields() {
    const studentElements = document.querySelectorAll(".student-hidden");
    const studentDocElements = document.querySelectorAll(".doc2-hidden");

    if (checkbox.checked) {
      studentElements.forEach(el => el.classList.add("d-none"));
      studentDocElements.forEach(el => el.classList.add("d-none"));
      hiddenField.value = "1";
    } else {
      studentElements.forEach(el => el.classList.remove("d-none"));
      hiddenField.value = "0";

      // Показываем поля документа ученика, если выбран тип
      if (studentDocType.value !== "") {
        studentDocElements.forEach(el => el.classList.remove("d-none"));
      }
    }
  }

  checkbox.addEventListener("change", toggleStudentFields);
  toggleStudentFields(); // инициализация при загрузке

  // Подстановка API-данных
  document.getElementById("fetchApiButton").addEventListener("click", async function () {
    const year = document.getElementById("api_year").value;
    const id = document.getElementById("api_id").value;
    const subdomain = document.getElementById("api_subdomain").value;
    const login = document.getElementById("api_login").value;
    const password = document.getElementById("api_password").value;

    if (!year || !id || !subdomain || !login || !password) {
      alert("Введите данные для запроса к ХХ");
      return;
    }

    const formData = new FormData();
    formData.append("year", year);
    formData.append("id", id);
    formData.append("subdomain", subdomain);
    formData.append("login", login);
    formData.append("password", password);

    try {
      const response = await fetch("/fetch_data", {
        method: "POST",
        body: formData
      });

      if (response.ok) {
        const data = await response.json();

        for (const key in data) {
          const field = document.getElementById(key);
          if (field) {
            if (field.type === "checkbox") {
              field.checked = data[key] === "true";
            } else {
              field.value = data[key];
            }
            localStorage.setItem(field.name, data[key]);
          }
        }

        if ("same_person" in data) {
          checkbox.checked = data["same_person"] === "1";
          hiddenField.value = data["same_person"];
          toggleStudentFields();
        }

        if (payerDocType.value !== "") {
          payerDocFields.forEach(el => el.classList.remove("d-none"));
          payerDocSeries?.setAttribute("required", "true");
        }

        if (!checkbox.checked && studentDocType.value !== "") {
          studentDocFields.forEach(el => el.classList.remove("d-none"));
          studentDocSeries?.setAttribute("required", "true");
        }

      } else {
        alert("Ошибка при получении данных из API");
      }
    } catch (error) {
      console.error("Ошибка запроса:", error);
      alert("Ошибка выполнения запроса к API");
    }
  });

  // Обработчики изменения типа документа
  payerDocType.addEventListener("change", function () {
    if (this.value !== "") {
      payerDocFields.forEach(el => el.classList.remove("d-none"));
      payerDocSeries?.setAttribute("required", "true");
    } else {
      payerDocFields.forEach(el => el.classList.add("d-none"));
      payerDocSeries?.removeAttribute("required");
    }
  });

  studentDocType.addEventListener("change", function () {
    if (checkbox.checked) {
      // Не показываем поля документа, если чекбокс включён
      studentDocFields.forEach(el => el.classList.add("d-none"));
      studentDocSeries?.removeAttribute("required");
      return;
    }

    if (this.value !== "") {
      studentDocFields.forEach(el => el.classList.remove("d-none"));
      studentDocSeries?.setAttribute("required", "true");
    } else {
      studentDocFields.forEach(el => el.classList.add("d-none"));
      studentDocSeries?.removeAttribute("required");
    }
  });
});