(function(){
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".skills-container[data-add-url]").forEach(initSkills);

    function initSkills(container) {
      const block = container.closest(".skills-block") || container.parentElement;
      const skillsUrl = container.dataset.searchUrl;
      const addUrl = container.dataset.addUrl;
      const removeUrl = (skillId) => container.dataset.removeUrl.replace("/0/remove/", `/${skillId}/remove/`);

      const addBtn = block.querySelector(".add-skill-btn");
      const inputWrapper = block.querySelector(".skill-input-wrapper");
      const input = block.querySelector(".skill-input");
      const suggestions = block.querySelector(".skill-suggestions");

      if (!addBtn || !inputWrapper || !input || !suggestions) return;

      addBtn.addEventListener("click", () => {
        addBtn.classList.add("hidden");
        inputWrapper.classList.remove("hidden");
        input.value = "";
        suggestions.innerHTML = "";
        suggestions.classList.add("hidden");
        input.focus();
      });

      let timer = null;
      input.addEventListener("input", () => {
        const q = input.value.trim();
        clearTimeout(timer);
        if (!q) {
          suggestions.classList.add("hidden");
          suggestions.innerHTML = "";
          return;
        }
        timer = setTimeout(async () => {
          const res = await fetch(`${skillsUrl}?q=${encodeURIComponent(q)}`);
          if (!res.ok) return;
          const data = await res.json();

          suggestions.innerHTML = "";
          data.forEach(skill => {
            const li = document.createElement("li");
            li.textContent = skill.name;
            li.dataset.id = skill.id;
            li.className = "suggestion-item";
            suggestions.appendChild(li);
          });

          const exact = data.some(skill => skill.name.toLowerCase() === q.toLowerCase());
          if (!exact) {
            const liNew = document.createElement("li");
            liNew.textContent = `Создать «${q}»`;
            liNew.dataset.name = q;
            liNew.className = "create-new";
            suggestions.appendChild(liNew);
          }

          suggestions.classList.remove("hidden");
        }, 200);
      });

      suggestions.addEventListener("mousedown", async (e) => {
        const li = e.target.closest("li");
        if (!li) return;

        if (li.classList.contains("create-new")) {
          await addSkillByName(li.dataset.name);
        } else if (li.dataset.id) {
          await addSkillById(li.dataset.id);
        }
        hideInput();
      });

      input.addEventListener("keydown", async (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          const q = input.value.trim();
          if (!q) return;

          const first = suggestions.querySelector("li");
          if (first && first.dataset.id) {
            await addSkillById(first.dataset.id);
          } else {
            await addSkillByName(q);
          }
          hideInput();
        }
        if (e.key === "Escape") {
          hideInput();
        }
      });

      input.addEventListener("blur", () => setTimeout(hideInput, 120));

      container.addEventListener("click", async (e) => {
        if (e.target.classList.contains("remove-skill-btn")) {
          const chip = e.target.closest(".skill-chip");
          const skillId = chip.dataset.id;
          const res = await fetch(removeUrl(skillId), {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") }
          });
          if (res.ok) {
            chip.remove();
            showEmptyIfNeeded();
          }
        }
      });

      async function addSkillById(skillId) {
        const res = await fetch(addUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({ skill_id: skillId }),
        });
        if (res.ok) {
          const skill = await res.json();
          appendChip(skill.id, skill.name);
        }
      }

      async function addSkillByName(name) {
        const res = await fetch(addUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({ name }),
        });
        if (res.ok) {
          const skill = await res.json();
          appendChip(skill.id, skill.name);
        }
      }

      function appendChip(id, name) {
        if (container.querySelector(`.skill-chip[data-id="${id}"]`)) return;

        const chip = document.createElement("span");
        chip.className = "skill-chip";
        chip.dataset.id = id;
        chip.innerHTML = `${name} <button type="button" class="remove-skill-btn" aria-label="Удалить" title="Удалить">×</button>`;

        container.insertBefore(chip, addBtn);

        const empty = container.querySelector(".skill-empty");
        if (empty) empty.remove();
      }

      function hideInput() {
        inputWrapper.classList.add("hidden");
        suggestions.classList.add("hidden");
        addBtn.classList.remove("hidden");
      }

      function showEmptyIfNeeded() {
        if (container.querySelector(".skill-chip") || container.querySelector(".skill-empty")) return;
        const empty = document.createElement("span");
        empty.className = "skill-empty";
        empty.textContent = container.dataset.emptyText || "Навыки не указаны";
        container.insertBefore(empty, addBtn);
      }
    }

    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
          cookie = cookie.trim();
          if (cookie.startsWith(name + "=")) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  });
})();
