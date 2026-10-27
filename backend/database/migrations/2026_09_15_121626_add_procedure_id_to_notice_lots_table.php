<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('notice_lots', function (Blueprint $table) {
             $table->foreignId('procedure_id')->nullable()->constrained('procedures')->cascadeOnDelete();
             $table->index('procedure_id');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('notice_lots', function (Blueprint $table) {
            $table->dropConstrainedForeignId('procedure_id');
        });
    }
};
