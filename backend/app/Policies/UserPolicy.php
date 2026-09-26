<?php

namespace App\Policies;

use App\Models\User;

class UserPolicy
{
    public function viewAny(User $user): bool
    {
        return $user->isAdmin();
    }

    public function view(User $user, User $targetUser): bool
    {
        return $user->isAdmin();
    }

    public function update(User $user, User $targetUser): bool
    {
        return $user->isAdmin();
    }

    public function anonymize(User $requestToDeleteUser, User $targetUser): bool
    {
        return $requestToDeleteUser->isAdmin() || $requestToDeleteUser->id == $targetUser->id;
    }
}
