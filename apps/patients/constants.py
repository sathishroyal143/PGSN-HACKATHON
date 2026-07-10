"""Constants for the Patients module."""

# Blood groups
BLOOD_GROUP_A_POS = 'A+'
BLOOD_GROUP_A_NEG = 'A-'
BLOOD_GROUP_B_POS = 'B+'
BLOOD_GROUP_B_NEG = 'B-'
BLOOD_GROUP_AB_POS = 'AB+'
BLOOD_GROUP_AB_NEG = 'AB-'
BLOOD_GROUP_O_POS = 'O+'
BLOOD_GROUP_O_NEG = 'O-'
BLOOD_GROUP_UNKNOWN = 'UNKNOWN'

BLOOD_GROUP_CHOICES = [
    (BLOOD_GROUP_A_POS, 'A+'),
    (BLOOD_GROUP_A_NEG, 'A-'),
    (BLOOD_GROUP_B_POS, 'B+'),
    (BLOOD_GROUP_B_NEG, 'B-'),
    (BLOOD_GROUP_AB_POS, 'AB+'),
    (BLOOD_GROUP_AB_NEG, 'AB-'),
    (BLOOD_GROUP_O_POS, 'O+'),
    (BLOOD_GROUP_O_NEG, 'O-'),
    (BLOOD_GROUP_UNKNOWN, 'Unknown'),
]

# Gender
GENDER_MALE = 'MALE'
GENDER_FEMALE = 'FEMALE'
GENDER_OTHER = 'OTHER'

GENDER_CHOICES = [
    (GENDER_MALE, 'Male'),
    (GENDER_FEMALE, 'Female'),
    (GENDER_OTHER, 'Other'),
]

# Patient status
STATUS_ACTIVE = 'ACTIVE'
STATUS_INACTIVE = 'INACTIVE'
STATUS_DECEASED = 'DECEASED'

STATUS_CHOICES = [
    (STATUS_ACTIVE, 'Active'),
    (STATUS_INACTIVE, 'Inactive'),
    (STATUS_DECEASED, 'Deceased'),
]

# Insurance types
INSURANCE_GOVERNMENT = 'GOVERNMENT'
INSURANCE_PRIVATE = 'PRIVATE'
INSURANCE_CORPORATE = 'CORPORATE'
INSURANCE_NONE = 'NONE'

INSURANCE_TYPE_CHOICES = [
    (INSURANCE_GOVERNMENT, 'Government'),
    (INSURANCE_PRIVATE, 'Private'),
    (INSURANCE_CORPORATE, 'Corporate'),
    (INSURANCE_NONE, 'None'),
]

# Mobility levels
MOBILITY_INDEPENDENT = 'INDEPENDENT'
MOBILITY_ASSISTED = 'ASSISTED'
MOBILITY_WHEELCHAIR = 'WHEELCHAIR'
MOBILITY_BEDRIDDEN = 'BEDRIDDEN'

MOBILITY_CHOICES = [
    (MOBILITY_INDEPENDENT, 'Independent'),
    (MOBILITY_ASSISTED, 'Assisted'),
    (MOBILITY_WHEELCHAIR, 'Wheelchair'),
    (MOBILITY_BEDRIDDEN, 'Bedridden'),
]

# Max limits
MAX_PATIENTS_PER_FAMILY = 10

# Success messages
MSG_PATIENT_CREATED = 'Patient profile created successfully.'
MSG_PATIENT_UPDATED = 'Patient profile updated successfully.'
MSG_PATIENT_DELETED = 'Patient profile deleted successfully.'
MSG_VITAL_RECORDED = 'Vital signs recorded successfully.'
MSG_VITAL_DELETED = 'Vital record deleted successfully.'
MSG_INSURANCE_CREATED = 'Insurance details saved successfully.'
MSG_INSURANCE_UPDATED = 'Insurance details updated successfully.'
MSG_INSURANCE_DELETED = 'Insurance details deleted successfully.'

# Error messages
ERR_PATIENT_NOT_FOUND = 'Patient not found.'
ERR_PATIENT_LIMIT = f'Maximum {MAX_PATIENTS_PER_FAMILY} patients allowed per family.'
ERR_VITAL_NOT_FOUND = 'Vital record not found.'
ERR_INSURANCE_NOT_FOUND = 'Insurance record not found.'
ERR_INSURANCE_EXISTS = 'Active insurance already exists for this patient.'
ERR_NO_FAMILY_PROFILE = 'Family profile not found for this user.'
ERR_PERMISSION_DENIED = 'You do not have permission to access this patient.'
