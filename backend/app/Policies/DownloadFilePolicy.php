<?php

declare(strict_types=1);

namespace App\Policies;

use App\Models\DownloadedFile;
use App\Models\User;

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
