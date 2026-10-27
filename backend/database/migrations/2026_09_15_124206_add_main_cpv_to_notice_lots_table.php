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
             $table->foreign('main_cpv')->references('code')->on('cpv_codes')->nullOnDelete();
             $table->index('main_cpv');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('notice_lots', function (Blueprint $table) {
            $table->dropForeign(['main_cpv']);
            $table->dropIndex(['main_cpv']);
        });
    }
};
