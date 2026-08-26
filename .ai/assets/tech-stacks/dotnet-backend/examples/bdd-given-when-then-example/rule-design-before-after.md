# BDDfy Rule Design: Before and After

## Before: Rules Too Fine-Grained

```
Rule_Plan_creation_with_valid_id_name_and_user()
Rule_Plan_id_must_be_unique_within_the_system()
Rule_Plan_name_is_required_and_cannot_be_empty()
Rule_Plan_id_must_be_a_valid_non_empty_string()
Rule_A_user_can_own_multiple_plans_with_different_ids()
Rule_Different_users_can_create_plans_with_the_same_name()
```

Result:
- Many Rules with 1 scenario each
- Hard to navigate and maintain

## After: Rules with Meaningful Scope

```
Rule_Plan_must_have_a_valid_and_unique_identifier()
Rule_Plan_must_have_valid_name_and_owner_information()
Rule_Users_can_own_and_manage_multiple_plans()
```

Result:
- 3 Rules with 3-5 scenarios each
- Scenarios grouped by business intent

## Why This Is Better

1. Related scenarios are grouped under the same business rule.
2. Each Rule includes positive, negative, and edge cases.
3. Rule names are business-readable (not technical).

## Rule Granularity Checklist

- Does the Rule represent a single business concept?
- Does it group 3-5 related scenarios?
- Are Rule names phrased in business language?

## Example Refactor (Tag Creation)

Before:
```
Rule_A_tag_can_be_created_with_valid_id_name_color_and_plan()
Rule_Tag_color_must_be_a_valid_hex_format()
```

After:
```
Rule_Tag_must_have_valid_properties_and_belong_to_a_plan()
```

Scenarios under the Rule:
- create_a_tag_successfully
- create_tag_with_invalid_color_format
- create_tag_with_null_name
- create_tag_with_empty_name
- create_multiple_tags_for_same_plan
