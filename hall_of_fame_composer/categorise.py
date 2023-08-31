import dotenv, os, yaml, re, unidecode
dotenv.load_dotenv()

DATA_PATH = os.getenv("DATA_PATH")
OUT_PATH = os.getenv("OUT_PATH")
in_file = os.path.join(OUT_PATH, 'gs_projects.yaml')
out_file = os.path.join(OUT_PATH, 'categorised.yaml')

def refine_origin(parsed: dict):
  if not parsed['origin']:
    return parsed
  match = re.match(r'SCP-(\d+)', parsed['origin'])
  if match:
    scp_number = int(match.group(1))
    with open(os.path.join(DATA_PATH, 'ab_proposals.txt')) as f:
      lines = f.readlines()
    file_name = lines[scp_number-1].strip()
    url = f'https://github.com/scalacenter/advisoryboard/blob/main/proposals/{file_name}'
    parsed['origin'] = url
  else:
    parsed['origin'] = None
  return parsed

def refine_contributors(parsed: dict):
  def regularize_name(name: str):
    name = name.lower()
    name = unidecode.unidecode(name)  # é -> e
    return name

  with open(os.path.join(DATA_PATH, 'contributors.yml')) as f:
    contributors = yaml.safe_load(f)

  # For each contributor in parsed, find them by name and replace with github username
  for i, contributor in enumerate(parsed['contributors']):
    for c in contributors['members']:
      if regularize_name(c['name']) == regularize_name(contributor):
        parsed['contributors'][i] = c['member']
        break
  return parsed

def refine_description(parsed: dict):
  if not parsed['description']:
    return parsed
  if (
      parsed['description'].lower().startswith('Main URL'.lower()) or
      parsed['description'].lower().startswith('Project Title'.lower())
    ):
    parsed['description'] = ""
  return parsed

def refine_impact(parsed: dict):
  if not parsed['impact']:
    return parsed
  if parsed['impact'].lower() == 'success':
    parsed['impact'] = None
  return parsed

def refine(parsed: dict):
  parsed = refine_origin(parsed)
  parsed = refine_contributors(parsed)
  parsed = refine_description(parsed)
  parsed = refine_impact(parsed)
  return parsed


def categorise_projects(projects: dict) -> dict:
  categories = []
  for project in projects:
    category_name = project['category'].capitalize()
    # Find the category
    category = None
    for c in categories:
      if c['name'] == category_name:
        category = c
        break
    if category is None:
      category = { 'name': category_name, 'projects': [] }
      categories.append(category)
    del project['category']
    refined = refine(project)
    category['projects'].append(refined)
  return categories

def process_projects():
  with open(in_file, 'r') as f:
    projects = yaml.safe_load(f)
  categories = categorise_projects(projects)
  with open(out_file, 'w') as f:
    yaml.dump(categories, f, sort_keys=False)

if __name__ == '__main__':
  process_projects()
