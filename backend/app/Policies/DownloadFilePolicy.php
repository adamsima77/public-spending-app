<?php

namespace App\Policies;

use App\Models\User;
use App\Models\DownloadedFile;

class DownloadFilePolicy
{
    public function viewAny(User $user): bool
    {
        return $user->isAdmin();
    }

    public function view(User $user, DownloadedFile $downloadedFile): bool
    {
        return $user->isAdmin();
    }
}
