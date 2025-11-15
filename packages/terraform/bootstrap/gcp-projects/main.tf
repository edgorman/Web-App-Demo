resource "google_project" "projects" {
  for_each   = { for project in var.projects : project.id_suffix => project }
  name       = "${var.projects_base_name} ${each.value.name_suffix}"
  project_id = "${var.projects_base_id}-${each.value.id_suffix}"
}
