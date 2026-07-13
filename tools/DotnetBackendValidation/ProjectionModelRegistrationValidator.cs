using System;
using System.Collections.Generic;
using System.Linq;

namespace DotnetBackendValidation;

public static class ProjectionModelRegistrationValidator
{
    public static IReadOnlyList<Type> FindUnregistered(
        IEnumerable<Type> candidateTypes,
        Type markerInterface,
        Func<Type, bool> isRegistered)
    {
        if (candidateTypes is null)
        {
            throw new ArgumentNullException(nameof(candidateTypes));
        }

        if (markerInterface is null)
        {
            throw new ArgumentNullException(nameof(markerInterface));
        }

        if (isRegistered is null)
        {
            throw new ArgumentNullException(nameof(isRegistered));
        }

        if (!markerInterface.IsInterface)
        {
            throw new ArgumentException("Projection marker must be an interface.", nameof(markerInterface));
        }

        return candidateTypes
            .Where(type =>
                type.IsClass
                && !type.IsAbstract
                && markerInterface.IsAssignableFrom(type)
                && !isRegistered(type))
            .OrderBy(type => type.FullName, StringComparer.Ordinal)
            .ToArray();
    }
}
