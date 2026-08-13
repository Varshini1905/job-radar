/* Study Squad — shared, live-synced learning room.
   Requires firebase-config.js to be filled in (see README "Study Squad Setup"). */

// Curated starter resources per skill group — always shown, even before anyone adds their own.
const STARTER_RESOURCES = {
  cloud: [
    { title: "LearnToCloud — full curriculum (free, structured)", url: "https://learntocloud.guide/curriculum" },
    { title: "AWS Cloud Practitioner Essentials (free, official)", url: "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/" },
    { title: "freeCodeCamp — AWS Cloud Practitioner full course (free, YouTube, 14h)", url: "https://www.freecodecamp.org/news/aws-certified-cloud-practitioner-study-course-pass-the-exam-with-this-free-13-hour-course/" },
    { title: "Cloud Resume Challenge (free, portfolio project)", url: "https://cloudresumechallenge.dev/docs/the-challenge/aws/" },
    { title: "HashiCorp Terraform tutorials (free, official)", url: "https://developer.hashicorp.com/terraform/tutorials" },
  ],
  cybersecurity: [
    { title: "TryHackMe — Pre Security path (free tier)", url: "https://tryhackme.com/path/outline/presecurity" },
    { title: "TryHackMe — SOC Level 1 path (free tier)", url: "https://tryhackme.com/path/outline/soclevel1" },
    { title: "Professor Messer — free Security+ SY0-701 course (blog + video)", url: "https://www.professormesser.com/security-plus/sy0-701/sy0-701-video/sy0-701-comptia-security-plus-course/" },
    { title: "Hack The Box Academy (free tier)", url: "https://academy.hackthebox.com/" },
    { title: "NetworkChuck — Cybersecurity full course (free, YouTube)", url: "https://www.youtube.com/@NetworkChuck" },
  ],
  devops: [
    { title: "Docker — Get Started guide (free, official)", url: "https://docs.docker.com/get-started/" },
    { title: "GitHub Actions docs (free, official)", url: "https://docs.github.com/en/actions" },
    { title: "Kubernetes basics tutorial (free, official)", url: "https://kubernetes.io/docs/tutorials/kubernetes-basics/" },
    { title: "TechWorld with Nana — DevOps roadmap (free, YouTube)", url: "https://www.youtube.com/@TechWorldwithNana" },
  ],
  servicenow: [
    { title: "NowLearning — free ServiceNow training (official)", url: "https://nowlearning.servicenow.com/" },
  ],
};

const GROUP_LABELS = {
  cloud: "Cloud",
  cybersecurity: "Cybersecurity",
  devops: "DevOps",
  servicenow: "ServiceNow",
};

let db = null;
let firebaseReady = false;

function initFirebase() {
  try {
    if (typeof firebaseConfig === "undefined" || firebaseConfig.apiKey.startsWith("PASTE_")) {
      firebaseReady = false;
      return;
    }
    firebase.initializeApp(firebaseConfig);
    db = firebase.firestore();
    firebaseReady = true;
  } catch (e) {
    console.error("Firebase init failed:", e);
    firebaseReady = false;
  }
}

function showSetupNotice() {
  document.getElementById("squad-setup-notice").style.display = "block";
  document.getElementById("squad-content").style.display = "none";
}

// ---------- Members ----------
function renderMembers(members) {
  const list = document.getElementById("squad-members-list");
  if (!members.length) {
    list.innerHTML = '<span class="empty-inline">No members yet — add yourself first.</span>';
    return;
  }
  list.innerHTML = members.map(m => `<span class="member-chip">${m.name}</span>`).join("");
}

function addMember() {
  const input = document.getElementById("new-member-name");
  const name = input.value.trim();
  if (!name || !db) return;
  db.collection("squad_members").add({ name, addedAt: Date.now() });
  input.value = "";
}

// ---------- Resources ----------
function renderResources(group, communityResources) {
  const starter = STARTER_RESOURCES[group] || [];
  const combined = [
    ...starter.map(r => ({ ...r, source: "curated" })),
    ...communityResources.map(r => ({ ...r, source: "community" })),
  ];
  const container = document.getElementById(`resources-${group}`);
  if (!container) return;
  container.innerHTML = combined.map(r => `
    <div class="resource-row">
      <a href="${r.url}" target="_blank" rel="noopener">${r.title}</a>
      ${r.source === "community" ? `<span class="added-by">added by ${r.addedBy || "someone"}</span>` : `<span class="added-by curated-tag">curated</span>`}
    </div>
  `).join("");
}

function addResource(group) {
  const titleInput = document.getElementById(`res-title-${group}`);
  const urlInput = document.getElementById(`res-url-${group}`);
  const byInput = document.getElementById("your-name-select");
  const title = titleInput.value.trim();
  const url = urlInput.value.trim();
  const addedBy = byInput ? byInput.value : "";
  if (!title || !url || !db) return;
  db.collection("squad_resources").add({ group, title, url, addedBy, addedAt: Date.now() });
  titleInput.value = "";
  urlInput.value = "";
}

function toggleGroup(group) {
  const el = document.getElementById(`group-${group}`);
  el.classList.toggle("expanded");
}

// jump here from the Skill Trends tab
function openSkillGroup(group) {
  document.querySelector('[data-view="squad"]').click();
  setTimeout(() => {
    const el = document.getElementById(`group-${group}`);
    if (el) {
      el.classList.add("expanded");
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, 100);
}

// ---------- Certifications ----------
function renderCertifications(certs, members) {
  const list = document.getElementById("squad-certs-list");
  if (!certs.length) {
    list.innerHTML = '<span class="empty-inline">No certifications being tracked yet.</span>';
    return;
  }
  list.innerHTML = certs.map(c => `
    <div class="item">
      <div>
        <div class="item-topic">${c.name}</div>
        <div class="item-resource">${c.owner || "unassigned"}</div>
      </div>
      <span class="status-badge status-${c.status}">${c.status.replace("_", " ")}</span>
    </div>
  `).join("");
}

function addCertification() {
  const nameInput = document.getElementById("new-cert-name");
  const ownerSelect = document.getElementById("your-name-select");
  const name = nameInput.value.trim();
  if (!name || !db) return;
  db.collection("squad_certifications").add({
    name, owner: ownerSelect ? ownerSelect.value : "", status: "not_started", addedAt: Date.now(),
  });
  nameInput.value = "";
}

// ---------- Live sync ----------
function attachListeners() {
  db.collection("squad_members").orderBy("addedAt").onSnapshot(snap => {
    const members = snap.docs.map(d => d.data());
    renderMembers(members);
    populateNameSelect(members);
  });

  db.collection("squad_resources").orderBy("addedAt").onSnapshot(snap => {
    const all = snap.docs.map(d => d.data());
    Object.keys(GROUP_LABELS).forEach(group => {
      renderResources(group, all.filter(r => r.group === group));
    });
  });

  db.collection("squad_certifications").orderBy("addedAt").onSnapshot(snap => {
    const certs = snap.docs.map((d) => ({ id: d.id, ...d.data() }));
    renderCertifications(certs);
  });
}

function populateNameSelect(members) {
  const select = document.getElementById("your-name-select");
  if (!select) return;
  const current = select.value;
  select.innerHTML = members.map(m => `<option value="${m.name}">${m.name}</option>`).join("");
  if (current) select.value = current;
}

function buildGroupSections() {
  const container = document.getElementById("squad-resource-groups");
  container.innerHTML = Object.entries(GROUP_LABELS).map(([key, label]) => `
    <div class="squad-group" id="group-${key}">
      <button class="squad-group-header" onclick="toggleGroup('${key}')">
        <span>${label}</span><span class="chevron">▾</span>
      </button>
      <div class="squad-group-body">
        <div id="resources-${key}" class="resource-list"></div>
        <div class="add-resource-row">
          <input type="text" id="res-title-${key}" placeholder="Resource name" />
          <input type="text" id="res-url-${key}" placeholder="https://..." />
          <button onclick="addResource('${key}')">Add</button>
        </div>
      </div>
    </div>
  `).join("");
}

function initStudySquad() {
  initFirebase();
  if (!firebaseReady) {
    showSetupNotice();
    return;
  }
  buildGroupSections();
  attachListeners();
}

document.addEventListener("DOMContentLoaded", initStudySquad);
