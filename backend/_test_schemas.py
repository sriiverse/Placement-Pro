import sys
sys.path.insert(0, '.')
from app.schemas import ProfileSchema, UserIdSchema, DashboardSchema, format_validation_errors
from pydantic import ValidationError

ok = True

# Test 1 - valid profile
try:
    p = ProfileSchema(
        full_name='Alice Smith',
        target_designation='Software Engineer',
        cgpa=8.5, grad_year=2025, branch='CSE',
        skills=['Python', 'React'],
        internships_count=1, projects_count=2
    )
    assert p.full_name == 'Alice Smith' and p.cgpa == 8.5
    print('PASS: valid ProfileSchema')
except Exception as e:
    print('FAIL: valid ProfileSchema -', e); ok = False

# Test 2 - CGPA out of range
try:
    ProfileSchema(full_name='Bob', target_designation='Eng', cgpa=11.0, grad_year=2025, branch='CSE', skills=['Python'])
    print('FAIL: CGPA>10 not caught'); ok = False
except ValidationError as e:
    errs = format_validation_errors(e)
    if any('cgpa' in err for err in errs):
        print('PASS: CGPA out-of-range rejected')
    else:
        print('FAIL: wrong error for CGPA -', errs); ok = False

# Test 3 - name with digits
try:
    ProfileSchema(full_name='B0b123', target_designation='Eng', cgpa=7.5, grad_year=2025, branch='CSE', skills=['Python'])
    print('FAIL: numeric name not caught'); ok = False
except ValidationError as e:
    errs = format_validation_errors(e)
    if any('full_name' in err for err in errs):
        print('PASS: name with digits rejected')
    else:
        print('FAIL: wrong error for name -', errs); ok = False

# Test 4 - empty skills
try:
    ProfileSchema(full_name='Alice', target_designation='Eng', cgpa=7.5, grad_year=2025, branch='CSE', skills=[])
    print('FAIL: empty skills not caught'); ok = False
except ValidationError as e:
    errs = format_validation_errors(e)
    if any('skill' in err.lower() for err in errs):
        print('PASS: empty skills rejected')
    else:
        print('FAIL: wrong error for skills -', errs); ok = False

# Test 5 - UserIdSchema invalid
try:
    UserIdSchema(user_id=0)
    print('FAIL: user_id=0 not caught'); ok = False
except ValidationError:
    print('PASS: user_id=0 rejected')

# Test 6 - DashboardSchema
d = DashboardSchema(user_id=1)
if d.simulated_skills is None:
    print('PASS: DashboardSchema default sim_skills=None')
else:
    print('FAIL: expected None sim_skills'); ok = False

# Full app factory check
from app import create_app
app = create_app()
print('PASS: app factory with Pydantic schemas loaded OK')

sys.exit(0 if ok else 1)
