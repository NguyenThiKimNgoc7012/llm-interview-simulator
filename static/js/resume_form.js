// Di chuyển phần bất kỳ section (Skills, Work Experience, Project, Education) lên
function moveSectionUp(button) {
  const section = button.closest('.section-card'); // Lấy phần section mà người dùng nhấn
  const prevSection = section.previousElementSibling; // Lấy phần tử trước đó trong DOM
  const previewSection = document.getElementById('preview_${section.id}'); // Tìm phần tử preview tương ứng

  // Kiểm tra xem phần tử trước đó có tồn tại không và di chuyển lên
  if (prevSection) {
    section.parentNode.insertBefore(section, prevSection); // Di chuyển phần lên
    previewSection.parentNode.insertBefore(previewSection, previewSection.previousElementSibling); // Di chuyển phần preview lên
  }
}

// Di chuyển phần bất kỳ section (Skills, Work Experience, Project, Education) xuống
function moveSectionDown(button) {
  const section = button.closest('.section-card'); // Lấy phần section mà người dùng nhấn
  const nextSection = section.nextElementSibling; // Lấy phần tử tiếp theo trong DOM
  const previewSection = document.getElementById('preview_${section.id}'); // Tìm phần tử preview tương ứng

  // Kiểm tra xem phần tử tiếp theo có tồn tại không và di chuyển xuống
  if (nextSection) {
    section.parentNode.insertBefore(nextSection, section); // Di chuyển phần xuống
    previewSection.parentNode.insertBefore(previewSection, previewSection.nextElementSibling); // Di chuyển phần preview xuống
  }
}




// Cập nhật preview ngay khi người dùng thay đổi thông tin
function updatePreview() {
  const name = document.getElementById("name")?.value || "";
  const position = document.getElementById("position")?.value || "";
  const phone = document.getElementById("phone")?.value || "";
  const email = document.getElementById("email")?.value || "";
  const website = document.getElementById("website")?.value || "";
  const objective = document.getElementById("objective")?.value || "";

  // Cập nhật các phần tử trong preview
  const previewName = document.getElementById("preview_name");
  if (previewName) previewName.innerText = name || "Tên đầy đủ...";
  const previewPosition = document.getElementById("preview_position");
  if (previewPosition) previewPosition.innerText = position || "Vị trí ứng tuyển...";
  const previewPhone = document.getElementById("preview_phone");
  if (previewPhone) previewPhone.innerText = phone || "Số điện thoại...";
  const previewEmail = document.getElementById("preview_email");
  if (previewEmail) previewEmail.innerText = email || "Email...";
  const previewWebsite = document.getElementById("preview_website");
  if (previewWebsite) previewWebsite.innerText = website || "Website...";
  const previewObjective = document.getElementById("preview_objective1");
  if (previewObjective) previewObjective.innerText = objective || "Mục tiêu nghề nghiệp...";
}

function updateWorkExperience() {
  // Lấy giá trị từ các ô nhập liệu
  const company = document.getElementById("company")?.value || "";
  const jobDate = document.getElementById("job_date")?.value || "";
  const jobTitle = document.getElementById("job_title")?.value || "";
  const jobDesc = document.getElementById("job_desc_input")?.value || "";
  const generatedExperience = document.getElementById("generated_experience")?.value || "";

  // Cập nhật các phần tử trong phần preview (kiểm tra null trước khi set)
  const previewCompany = document.getElementById("preview_company");
  if (previewCompany) previewCompany.innerText = company || "Công ty...";
  const previewJobDate = document.getElementById("preview_job_date");
  if (previewJobDate) previewJobDate.innerText = jobDate || "Ngày làm việc...";
  const previewJobTitle = document.getElementById("preview_job_title");
  if (previewJobTitle) previewJobTitle.innerText = jobTitle || "Chức danh...";
  const previewGeneratedExp = document.getElementById("preview_generated_experience");
  if (previewGeneratedExp) previewGeneratedExp.innerText = generatedExperience || "Kinh nghiệm làm việc sẽ được tạo bởi AI...";
}

// Đã gán sự kiện trong DOMContentLoaded, không cần gán ngoài nữa



function updatePreviewEducation() {
  const school = document.getElementById("school")?.value || "";
  const eduDate = document.getElementById("edu_date")?.value || "";
  const major = document.getElementById("major")?.value || "";
  const gpa = document.getElementById("gpa")?.value || "";
  const additionalInfo = document.getElementById("additional_info")?.value || "";

  // Cập nhật các phần tử trong preview
  const previewSchool = document.getElementById("preview_school");
  if (previewSchool) previewSchool.innerText = school || "Trường học...";
  const previewEduDate = document.getElementById("preview_edu_date");
  if (previewEduDate) previewEduDate.innerText = eduDate || "Ngày tốt nghiệp...";
  const previewMajor = document.getElementById("preview_major");
  if (previewMajor) previewMajor.innerText = major || "Chuyên ngành...";
  const previewGpa = document.getElementById("preview_gpa");
  if (previewGpa) previewGpa.innerText = gpa || "GPA...";
  const previewAdditionalInfo = document.getElementById("preview_additional_info");
  if (previewAdditionalInfo) previewAdditionalInfo.innerText = additionalInfo || "Thông tin bổ sung...";
}

// Đã gán sự kiện trong DOMContentLoaded, không cần gán ngoài nữa



function updatePreviewProject() {
  const projectName = document.getElementById("project_name")?.value || "";
  const projectDate = document.getElementById("project_date")?.value || "";
  const projectDesc = document.getElementById("project_desc")?.value || "";

  // Cập nhật các phần tử trong preview
  const previewProjectName = document.getElementById("preview_project_name");
  if (previewProjectName) previewProjectName.innerText = projectName || "Tên dự án...";
  const previewProjectDate = document.getElementById("preview_project_date");
  if (previewProjectDate) previewProjectDate.innerText = projectDate || "Thời gian...";
  const previewProjectDesc = document.getElementById("preview_project_desc");
  if (previewProjectDesc) previewProjectDesc.innerText = projectDesc || "Mô tả dự án...";
}

// Gán sự kiện sau khi DOM đã load
document.addEventListener("DOMContentLoaded", function () {
  // Thông tin cá nhân
  const name = document.getElementById("name");
  const position = document.getElementById("position");
  const phone = document.getElementById("phone");
  const email = document.getElementById("email");
  const website = document.getElementById("website");
  const objective = document.getElementById("objective");
  if (name) name.addEventListener("input", updatePreview);
  if (position) position.addEventListener("input", updatePreview);
  if (phone) phone.addEventListener("input", updatePreview);
  if (email) email.addEventListener("input", updatePreview);
  if (website) website.addEventListener("input", updatePreview);
  if (objective) objective.addEventListener("input", updatePreview);

  // Work experience
  const company = document.getElementById("company");
  const job_date = document.getElementById("job_date");
  const job_title = document.getElementById("job_title");
  const job_desc_input = document.getElementById("job_desc_input");
  const generated_experience = document.getElementById("generated_experience");
  if (company) company.addEventListener("input", updateWorkExperience);
  if (job_date) job_date.addEventListener("input", updateWorkExperience);
  if (job_title) job_title.addEventListener("input", updateWorkExperience);
  if (job_desc_input) job_desc_input.addEventListener("input", updateWorkExperience);
  if (generated_experience) generated_experience.addEventListener("input", updateWorkExperience);

  // Education
  const school = document.getElementById("school");
  const edu_date = document.getElementById("edu_date");
  const major = document.getElementById("major");
  const gpa = document.getElementById("gpa");
  const additional_info = document.getElementById("additional_info");
  if (school) school.addEventListener("input", updatePreviewEducation);
  if (edu_date) edu_date.addEventListener("input", updatePreviewEducation);
  if (major) major.addEventListener("input", updatePreviewEducation);
  if (gpa) gpa.addEventListener("input", updatePreviewEducation);
  if (additional_info) additional_info.addEventListener("input", updatePreviewEducation);

  // Project
  const project_name = document.getElementById("project_name");
  const project_date = document.getElementById("project_date");
  const project_desc = document.getElementById("project_desc");
  if (project_name) project_name.addEventListener("input", updatePreviewProject);
  if (project_date) project_date.addEventListener("input", updatePreviewProject);
  if (project_desc) project_desc.addEventListener("input", updatePreviewProject);

  // AI generate objective
  const aiGenBtn = document.getElementById("ai-generate-btn");
  if (aiGenBtn) aiGenBtn.addEventListener("click", async function () {
    const objectiveVal = objective ? objective.value : "";
    console.log("Generating objective with:", objectiveVal);
    const response = await generateObjective(objectiveVal);
    const previewObj = document.getElementById("preview_objective1");
    const previewObj2 = document.getElementById("preview_objective");

    if (previewObj) previewObj.innerText = response || "Không có dữ liệu.";
    if (previewObj2) previewObj2.innerText = response || "Không có dữ liệu.";
    // Điền kết quả AI vào ô input objective
    if (objective) objective.value = response || "";
  });

  // AI generate experience
  const aiGenExpBtn = document.getElementById("ai-generate-btn-experience");
  if (aiGenExpBtn) aiGenExpBtn.addEventListener("click", async function () {
    const jobDesc = job_desc_input ? job_desc_input.value : "";
    console.log("Generating experience with:", jobDesc);
    const response = await generateExperience(jobDesc);
    const previewExp = document.getElementById("preview_generated_experience");
    const preview_experience = document.getElementById("preview_experience");
    if (previewExp) previewExp.innerText = response || "Không có dữ liệu.";
    if (preview_experience) preview_experience.innerText = response || "Không có dữ liệu.";
    if (generated_experience) generated_experience.value = response || "";
  });
});

// Hàm AI generate objective
async function generateObjective(objective) {
  try {
    const response = await fetch('/generate_objective', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: objective })
    });
    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error("Error generating objective:", error);
    return "Lỗi khi tạo mục tiêu nghề nghiệp.";
  }
}

// Hàm AI generate kinh nghiệm làm việc
async function generateExperience(jobDesc) {
  if (!jobDesc || jobDesc.trim() === "") {
    console.log("Vui lòng nhập mô tả công việc trước khi tạo kinh nghiệm AI!");
    return "";
  }
  try {
    const response = await fetch("/generate_experience", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        job_desc: jobDesc
      })
    });
    const data = await response.json();
    if (data.error) return data.error;
    return data.response;
  } catch (error) {
    console.error("Error generating experience:", error);
    return "Lỗi khi tạo kinh nghiệm làm việc.";
  }
}

// Hàm hiển thị toast message
function showToast(message, isSuccess = true) {
  const toastElement = document.getElementById('toastMsg');
  const toastBody = document.getElementById('toastBody');

  if (toastElement && toastBody) {
    toastBody.textContent = message;

    // Thay đổi màu sắc dựa trên trạng thái
    if (isSuccess) {
      toastElement.className = 'toast align-items-center text-white bg-success border-0';
    } else {
      toastElement.className = 'toast align-items-center text-white bg-danger border-0';
    }

    // Hiển thị toast
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
  }
}

// Hàm lưu CV vào database
async function saveCV() {
  try {
    const cvData = {
      name: document.getElementById("name")?.value || "",
      position: document.getElementById("position")?.value || "",
      phone: document.getElementById("phone")?.value || "",
      email: document.getElementById("email")?.value || "",
      website: document.getElementById("website")?.value || "",
      objective: document.getElementById("objective")?.value || "",
      company: document.getElementById("company")?.value || "",
      job_date: document.getElementById("job_date")?.value || "",
      job_title: document.getElementById("job_title")?.value || "",
      job_description: document.getElementById("job_desc_input")?.value || "",
      generated_experience: document.getElementById("generated_experience")?.value || "",
      school: document.getElementById("school")?.value || "",
      edu_date: document.getElementById("edu_date")?.value || "",
      major: document.getElementById("major")?.value || "",
      gpa: document.getElementById("gpa")?.value || "",
      project_name: document.getElementById("project_name")?.value || "",
      project_date: document.getElementById("project_date")?.value || "",
      project_desc: document.getElementById("project_desc")?.value || "",
      skills: document.querySelector('#skillsSection textarea')?.value || "",
      featured_skill1: document.getElementById("Featured_Skills1")?.value || "",
      featured_skill2: document.getElementById("Featured_Skills2")?.value || ""
    };

    // Kiểm tra dữ liệu cơ bản
    if (!cvData.name.trim()) {
      showToast("Vui lòng nhập tên trước khi lưu CV!", false);
      return;
    }

    const response = await fetch("/save_cv", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(cvData)
    });

    const result = await response.json();

    if (result.success) {
      showToast("CV đã được lưu thành công!", true);
      console.log("CV saved with ID:", result.cv_id);
    } else {
      showToast("Lỗi khi lưu CV: " + (result.error || "Không xác định"), false);
    }
  } catch (error) {
    console.error("Error saving CV:", error);
    showToast("Đã xảy ra lỗi khi lưu CV. Vui lòng thử lại.", false);
  }
}

// Hàm download CV dưới dạng PDF
async function downloadResume() {
  try {
    const cvData = {
      name: document.getElementById("name")?.value || "",
      position: document.getElementById("position")?.value || "",
      phone: document.getElementById("phone")?.value || "",
      email: document.getElementById("email")?.value || "",
      website: document.getElementById("website")?.value || "",
      objective: document.getElementById("objective")?.value || "",
      company: document.getElementById("company")?.value || "",
      job_date: document.getElementById("job_date")?.value || "",
      job_title: document.getElementById("job_title")?.value || "",
      job_description: document.getElementById("job_desc_input")?.value || "",
      generated_experience: document.getElementById("generated_experience")?.value || "",
      school: document.getElementById("school")?.value || "",
      edu_date: document.getElementById("edu_date")?.value || "",
      major: document.getElementById("major")?.value || "",
      gpa: document.getElementById("gpa")?.value || "",
      project_name: document.getElementById("project_name")?.value || "",
      project_date: document.getElementById("project_date")?.value || "",
      project_desc: document.getElementById("project_desc")?.value || "",
      skills: document.querySelector('#skillsSection textarea')?.value || "",
      featured_skill1: document.getElementById("Featured_Skills1")?.value || "",
      featured_skill2: document.getElementById("Featured_Skills2")?.value || ""
    };

    // Kiểm tra dữ liệu cơ bản
    if (!cvData.name.trim()) {
      showToast("Vui lòng nhập tên trước khi tạo CV!", false);
      return;
    }

    // Hiển thị loading state
    showToast("Đang tạo CV...", true);

    const response = await fetch("/download_cv", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(cvData)
    });

    if (response.ok) {
      // Tạo blob từ response
      const blob = await response.blob();

      // Tạo URL tạm thời cho blob
      const url = window.URL.createObjectURL(blob);

      // Tạo link download
      const link = document.createElement('a');
      link.href = url;

      // Lấy tên file từ header hoặc tạo tên mặc định
      const contentDisposition = response.headers.get('content-disposition');
      let filename = `CV_${cvData.name.replace(/\s+/g, '_')}_${new Date().toISOString().slice(0, 10)}.pdf`;
      if (contentDisposition) {
        const matches = contentDisposition.match(/filename="([^"]+)"/);
        if (matches) filename = matches[1];
      }

      link.download = filename;
      document.body.appendChild(link);
      link.click();

      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      showToast("CV đã được tải xuống thành công!", true);
      console.log("CV downloaded successfully!");
    } else {
      const errorData = await response.json();
      showToast("Lỗi khi tạo CV: " + (errorData.error || "Không xác định"), false);
    }
  } catch (error) {
    console.error("Error downloading CV:", error);
    showToast("Đã xảy ra lỗi khi tạo CV. Vui lòng thử lại.", false);
  }
}

function removeVietnameseTones(str) {
  str = str.normalize('NFD') // chuyển các ký tự có dấu thành tổ hợp (dấu + chữ)
    .replace(/[\u0300-\u036f]/g, '') // xóa dấu
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D');
  return str;
}

// Download CV ở FE bằng jsPDF
function downloadResumeFE() {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  // Lấy dữ liệu từ form
  const name = removeVietnameseTones(document.getElementById("name")?.value || "");
  const position = removeVietnameseTones(document.getElementById("position")?.value || "");
  const phone = removeVietnameseTones(document.getElementById("phone")?.value || "");
  const email = removeVietnameseTones(document.getElementById("email")?.value || "");
  const website = removeVietnameseTones(document.getElementById("website")?.value || "");
  const objective = removeVietnameseTones(document.getElementById("objective")?.value || "");
  const company = removeVietnameseTones(document.getElementById("company")?.value || "");
  const job_date = removeVietnameseTones(document.getElementById("job_date")?.value || "");
  const job_title = removeVietnameseTones(document.getElementById("job_title")?.value || "");
  const generated_experience = removeVietnameseTones(document.getElementById("generated_experience")?.value || "");
  const school = removeVietnameseTones(document.getElementById("school")?.value || "");
  const edu_date = removeVietnameseTones(document.getElementById("edu_date")?.value || "");
  const major = removeVietnameseTones(document.getElementById("major")?.value || "");
  const gpa = removeVietnameseTones(document.getElementById("gpa")?.value || "");
  const project_name = removeVietnameseTones(document.getElementById("project_name")?.value || "");
  const project_date = removeVietnameseTones(document.getElementById("project_date")?.value || "");
  const project_desc = removeVietnameseTones(document.getElementById("project_desc")?.value || "");
  const skills = removeVietnameseTones(document.querySelector('#skillsSection textarea')?.value || "");
  const featured_skill1 = removeVietnameseTones(document.getElementById("Featured_Skills1")?.value || "");
  const featured_skill2 = removeVietnameseTones(document.getElementById("Featured_Skills2")?.value || "");

  let y = 15;
  doc.setFontSize(18);
  doc.text(name, 105, y, { align: 'center' });
  y += 10;
  doc.setFontSize(12);
  doc.text(`${position} | ${phone} | ${email}${website ? ' | ' + website : ''}`, 105, y, { align: 'center' });
  y += 10;

  // Objective
  if (objective) {
    doc.setFontSize(14);
    doc.text('OBJECTIVE', 10, y);
    y += 7;
    doc.setFontSize(11);
    y = addMultiline(doc, objective, 10, y, 180);
    y += 5;
  }

  // Work Experience
  if (company || job_title) {
    doc.setFontSize(14);
    doc.text('WORK EXPERIENCE', 10, y);
    y += 7;
    doc.setFontSize(11);
    if (company) { doc.text(`Company: ${company}`, 10, y); y += 6; }
    if (job_title) { doc.text(`Position: ${job_title}`, 10, y); y += 6; }
    if (job_date) { doc.text(`Duration: ${job_date}`, 10, y); y += 6; }
    if (generated_experience) { y = addMultiline(doc, `Description: ${generated_experience}`, 10, y, 180); }
    y += 5;
  }

  // Education
  if (school || major) {
    doc.setFontSize(14);
    doc.text('EDUCATION', 10, y);
    y += 7;
    doc.setFontSize(11);
    if (school) { doc.text(`School: ${school}`, 10, y); y += 6; }
    if (major) { doc.text(`Major: ${major}`, 10, y); y += 6; }
    if (edu_date) { doc.text(`Graduation: ${edu_date}`, 10, y); y += 6; }
    if (gpa) { doc.text(`GPA: ${gpa}`, 10, y); y += 6; }
    y += 5;
  }

  // Projects
  if (project_name) {
    doc.setFontSize(14);
    doc.text('PROJECTS', 10, y);
    y += 7;
    doc.setFontSize(11);
    doc.text(`Project: ${project_name}`, 10, y); y += 6;
    if (project_date) { doc.text(`Duration: ${project_date}`, 10, y); y += 6; }
    if (project_desc) { y = addMultiline(doc, `Description: ${project_desc}`, 10, y, 180); }
    y += 5;
  }

  // Skills
  if (skills || featured_skill1 || featured_skill2) {
    doc.setFontSize(14);
    doc.text('SKILLS', 10, y);
    y += 7;
    doc.setFontSize(11);
    if (skills) { y = addMultiline(doc, skills, 10, y, 180); }
    if (featured_skill1) { doc.text(`Featured Skill 1: ${featured_skill1}`, 10, y); y += 6; }
    if (featured_skill2) { doc.text(`Featured Skill 2: ${featured_skill2}`, 10, y); y += 6; }
  }

  doc.save(`CV_${name.replace(/\s+/g, '_')}.pdf`);
}

// Helper để xuống dòng tự động
function addMultiline(doc, text, x, y, maxWidth) {
  const lines = doc.splitTextToSize(text, maxWidth);
  lines.forEach(line => {
    doc.text(line, x, y);
    y += 6;
  });
  return y;
}
