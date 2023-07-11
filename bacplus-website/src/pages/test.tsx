import { Prisma } from "@prisma/client";
import type { InferGetStaticPropsType, GetStaticProps } from "next";
import { prisma } from "~/server/db";

export const getStaticProps: GetStaticProps<{
  top_licee: any[];
}> = async () => {
  const judete = {} as any;

  (
    await prisma.elevi.groupBy({
      by: ["id_judet", "an"],
      _count: {
        my_medie: true,
      },
      _avg: {
        my_medie: true,
      },
    })
  ).forEach((result) => {
    if (result.id_judet === null) return;

    if (judete[result.an] === undefined) {
      judete[result.an] = {};
    }

    if (judete[result.an][result.id_judet] === undefined) {
      judete[result.an][result.id_judet] = {
        medie: result._avg.my_medie,
        candidati: result._count.my_medie,
        promovati: 0,
      };
    }
  });

  (
    await prisma.elevi.groupBy({
      by: ["id_judet", "an"],
      _count: {
        _all: true,
      },
      where: {
        rezultat: "REUSIT",
      },
    })
  ).forEach((result) => {
    if (result.id_judet === null) return;

    judete[result.an][result.id_judet].promovati = result._count._all;
  });

  return {
    props: {
      top_licee: judete,
    },
  };
};

export default function Page({
  top_licee,
}: InferGetStaticPropsType<typeof getStaticProps>) {
  return (
    <div className="p-4">
      {Object.entries(top_licee[2023]).map(
        ([id_judet, { medie, candidati, promovati }], ix) => (
          <p key={ix}>{`${id_judet} - medie ${
            Math.round(medie * 100) / 100
          }, promovare ${
            Math.round((promovati / candidati) * 100 * 10) / 10
          }%`}</p>
        )
      )}
    </div>
  );
}
