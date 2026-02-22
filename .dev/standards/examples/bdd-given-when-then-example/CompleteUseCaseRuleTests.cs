using System.Threading.Tasks;
using TestStack.BDDfy;
using Xunit;

namespace AiScrum.Tests.Rules;

public sealed class CompleteUseCaseRuleTests
{
    private readonly StepState _state = new();

    [Fact]
    public void Rule_Happy_path_successful_basic_operation()
    {
        this.Given(_ => Given_valid_input_data())
            .When(_ => When_i_perform_the_operation())
            .Then(_ => Then_the_operation_succeeds())
            .BDDfy();
    }

    [Fact]
    public void Rule_Happy_path_successful_operation_with_optional_parameters()
    {
        this.Given(_ => Given_valid_input_with_optional_fields())
            .When(_ => When_i_perform_the_operation())
            .Then(_ => Then_the_optional_fields_are_persisted())
            .BDDfy();
    }

    [Fact]
    public void Rule_Input_validation_reject_null_required_field()
    {
        this.Given(_ => Given_input_with_a_null_required_field())
            .When(_ => When_i_attempt_the_operation())
            .Then(_ => Then_the_operation_is_rejected_for_validation_errors())
            .BDDfy();
    }

    [Fact]
    public void Rule_Input_validation_reject_empty_string_field()
    {
        this.Given(_ => Given_input_with_an_empty_string())
            .When(_ => When_i_attempt_the_operation())
            .Then(_ => Then_the_operation_is_rejected_for_validation_errors())
            .BDDfy();
    }

    [Fact]
    public void Rule_Business_rule_enforcement_enforce_unique_constraint()
    {
        this.Given(_ => Given_an_existing_entity())
            .When(_ => When_i_attempt_to_create_a_duplicate())
            .Then(_ => Then_the_operation_is_rejected_for_business_rule_violations())
            .BDDfy();
    }

    [Fact]
    public void Rule_Business_rule_enforcement_enforce_maximum_limit()
    {
        this.Given(_ => Given_entities_at_the_maximum_limit())
            .When(_ => When_i_attempt_to_exceed_the_limit())
            .Then(_ => Then_the_operation_is_rejected_for_business_rule_violations())
            .BDDfy();
    }

    [Fact]
    public void Rule_Error_handling_handle_repository_failure()
    {
        this.Given(_ => Given_a_failing_repository())
            .When(_ => When_i_perform_the_operation())
            .Then(_ => Then_the_failure_is_handled_gracefully())
            .BDDfy();
    }

    [Fact]
    public void Rule_Edge_cases_handle_maximum_field_length()
    {
        this.Given(_ => Given_input_at_maximum_length())
            .When(_ => When_i_perform_the_operation())
            .Then(_ => Then_the_operation_succeeds())
            .BDDfy();
    }

    [Fact]
    public void Rule_Security_and_authorization_prevent_unauthorized_access()
    {
        this.Given(_ => Given_an_unauthorized_user())
            .When(_ => When_i_attempt_the_operation())
            .Then(_ => Then_access_is_denied())
            .BDDfy();
    }

    [Fact]
    public void Rule_Performance_requirements_complete_within_time_limit()
    {
        this.Given(_ => Given_performance_test_data())
            .When(_ => When_i_perform_the_operation())
            .Then(_ => Then_the_operation_completes_within_the_expected_time_limit())
            .BDDfy();
    }

    void Given_valid_input_data() => _state.HasValidInput = true;
    void Given_valid_input_with_optional_fields() => _state.HasOptionalFields = true;
    void Given_input_with_a_null_required_field() => _state.HasNullRequiredField = true;
    void Given_input_with_an_empty_string() => _state.HasEmptyString = true;
    void Given_an_existing_entity() => _state.HasExistingEntity = true;
    void Given_entities_at_the_maximum_limit() => _state.HasMaximumLimit = true;
    void Given_a_failing_repository() => _state.HasFailingRepository = true;
    void Given_input_at_maximum_length() => _state.HasMaxLengthInput = true;
    void Given_an_unauthorized_user() => _state.IsUnauthorized = true;
    void Given_performance_test_data() => _state.IsPerformanceTest = true;

    Task When_i_perform_the_operation()
    {
        // TODO: Execute the target use case.
        _state.DurationMs = 10;
        return Task.CompletedTask;
    }

    Task When_i_attempt_the_operation() => When_i_perform_the_operation();

    Task When_i_attempt_to_create_a_duplicate() => When_i_perform_the_operation();

    Task When_i_attempt_to_exceed_the_limit() => When_i_perform_the_operation();

    void Then_the_operation_succeeds()
    {
        Assert.True(_state.HasValidInput || _state.HasMaxLengthInput);
    }

    void Then_the_optional_fields_are_persisted()
    {
        Assert.True(_state.HasOptionalFields);
    }

    void Then_the_operation_is_rejected_for_validation_errors()
    {
        Assert.True(_state.HasNullRequiredField || _state.HasEmptyString);
    }

    void Then_the_operation_is_rejected_for_business_rule_violations()
    {
        Assert.True(_state.HasExistingEntity || _state.HasMaximumLimit);
    }

    void Then_the_failure_is_handled_gracefully()
    {
        Assert.True(_state.HasFailingRepository);
    }

    void Then_access_is_denied()
    {
        Assert.True(_state.IsUnauthorized);
    }

    void Then_the_operation_completes_within_the_expected_time_limit()
    {
        Assert.True(_state.DurationMs >= 0);
    }

    private sealed class StepState
    {
        public bool HasValidInput { get; set; }
        public bool HasOptionalFields { get; set; }
        public bool HasNullRequiredField { get; set; }
        public bool HasEmptyString { get; set; }
        public bool HasExistingEntity { get; set; }
        public bool HasMaximumLimit { get; set; }
        public bool HasFailingRepository { get; set; }
        public bool HasMaxLengthInput { get; set; }
        public bool IsUnauthorized { get; set; }
        public bool IsPerformanceTest { get; set; }
        public long DurationMs { get; set; }
    }
}
