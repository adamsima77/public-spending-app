<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class () extends Migration {
    public function up(): void
    {
        Schema::table('notices', function (Blueprint $table): void {
            $table->foreignId('procedure_id')->nullable()->constrained('procedures')->restrictOnDelete();
            $table->index('procedure_id');
        });
    }

    public function down(): void
    {
        Schema::table('notices', function (Blueprint $table): void {
            $table->dropConstrainedForeignId('procedure_id');
        });
    }
};
